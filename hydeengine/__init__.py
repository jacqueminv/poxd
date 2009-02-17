import imp
import sys
import os
import shutil
from datetime import datetime

from django.conf import settings
from django.core.management import setup_environ
from django.template import add_to_builtins
from django.template.loader import render_to_string

from path_util import PathUtil
from file_system import File, Folder
from processor import Processor
from siteinfo import SiteInfo

def setup_env(site_path):
    """
    
    Initializes Django Environment
    
    """
    try:
        imp.load_source("hyde_site_settings",
                        os.path.join(site_path,"settings.py"))
    except Exception, err:
        print "Cannot Import Site Settings"
        print err
        raise ValueError(
        "The given site_path [%s] does not contain a hyde site. \
        Give a valid path or run -init to create a new site."  
        %  site_path
        )
        
    try:
        os.environ['DJANGO_SETTINGS_MODULE'] = u"hyde_site_settings"
    except Exception, err:
        print "Site settings are not defined properly"
        print err
        raise ValueError(
        "The given site_path [%s] has invalid settings. \
        Give a valid path or run -init to create a new site."  
        %  site_path
        )

class Server(object):
    """
    
    Initializes and runs a cherrypy webserver servic static files from the deploy
    directory
    
    """
    def __init__(self, site_path):
        super(Server, self).__init__()
        self.site_path = os.path.abspath(os.path.expandvars(
                                        os.path.expanduser(site_path)))
    def serve(self, deploy_path):
        setup_env(self.site_path)
        deploy_folder = Folder(
                            (deploy_path, settings.DEPLOY_DIR)
                            [not deploy_path])
        import cherrypy
        from cherrypy.lib.static import serve_file
        
        class WebRoot:
            @cherrypy.expose
            def index(self):
                if not 'site' in settings.CONTEXT:
                    build_sitemap()
                page =  settings.CONTEXT['site'].listing_page
                return serve_file(deploy_folder.child(page.name))
            
        cherrypy.config.update({'environment': 'production',
                                  'log.error_file': 'site.log',
                                  'log.screen': True})
        conf = {'/': {
        'tools.staticdir.dir': deploy_folder.path, 
        'tools.staticdir.on':True
        }}
        cherrypy.quickstart(WebRoot(), '/', config = conf)
   

class Generator(object):
    def __init__(self, site_path):
        super(Generator, self).__init__()
        self.site_path = os.path.abspath(os.path.expandvars(
                                        os.path.expanduser(site_path)))
                                        
    # def start_processing(self, all_done, queue, process):
    #     while True:
    #         try:
    #             processable = queue.get(15)
    #             if processable['exception']:
    #                 raise processable['exception']
    #             resource = processable['resource']
    #             change = processable['change']
    #             process(resource, change)
    #         except Empty:
    #             # Nothing in the queue... check if we are all done.
    #             if all_done.isSet():
    #                 # Looks like we are done here. Break off.
    #                 break
    #                 
    # def generate_all(self):
    
    def process(self, resource, change="Added"):
        processor = Processor(settings) 
        settings.CONTEXT['node'] = resource.node
        settings.CONTEXT['resource'] = resource
        processor.process(resource)
        
    def build_siteinfo(self, deploy_path=None):
        tmp_folder = Folder(settings.TMP_DIR)
        deploy_folder = Folder(
                            (deploy_path, settings.DEPLOY_DIR)
                            [not deploy_path])
                            
        if deploy_folder.exists and settings.BACKUP:
            backup_folder = Folder(settings.BACKUPS_DIR).make()
            deploy_folder.backup(backup_folder)

        tmp_folder.delete()
        tmp_folder.make()
        settings.DEPLOY_DIR = deploy_folder.path
        add_to_builtins('hydeengine.templatetags.hydetags')
        add_to_builtins('hydeengine.templatetags.aym')
        
        self.siteinfo  = SiteInfo(settings, self.site_path)
        self.siteinfo.refresh()
        settings.CONTEXT['site'] = self.siteinfo.content_node

    def generate(self, deploy_path, keep_watching):
        baseline = datetime.now()
        self.build_siteinfo(deploy_path)
        for resource in self.site.walk_resources():
            self.process(resource)
        
        tmp_folder.delete()
    
class Initializer(object):
    def __init__(self, site_path):
        super(Initializer, self).__init__()
        self.site_path = Folder(site_path)

    def initialize(self, root, template=None, force=False):
        if not template:
            template = "default"
        root_folder = Folder(root)
            
        template_dir = root_folder.child_folder("templates", template)
        
        if not template_dir.exists:
            raise ValueError(
            "Cannot find the specified template[%s]." % template_dir)
            
        if self.site_path.exists:    
            files = os.listdir(self.site_path.path)
            PathUtil.filter_hidden_inplace(files)
            if len(files) and not force:
                raise ValueError(
                "The site_path[%s] is not empty." % self.site_path)
            else:
                self.site_path.delete()
        self.site_path.make()
        self.site_path.copy_contents_of(template_dir)