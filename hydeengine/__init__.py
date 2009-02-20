import imp
import sys
import os
import shutil
from datetime import datetime
from threading import Thread
from threading import Event
from Queue import Queue

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
    
    Initializes and runs a cherrypy webserver serving static files from the deploy
    folder
    
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
        self.regenerate_request = Event()    
        self.processor = Processor(settings)
    
    def process(self, resource, change="Added"):
        settings.CONTEXT['node'] = resource.node
        settings.CONTEXT['resource'] = resource
        self.processor.process(resource)
        
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
        
    def post_process(self, node):
        self.processor.post_process(self.siteinfo)
    
    def process_all(self):
        for resource in self.siteinfo.walk_resources():            
            self.process(resource)
        self.post_process(self.siteinfo)
        self.siteinfo.target_folder.copy_contents_of(
               self.siteinfo.temp_folder, incremental=True)
    
    def regenerator(self):
        pending = False
        while True:
            # Wait for the regeneration event to be set
            self.regenerate_request.wait(5)

            # Wait until there are no more requests            
            # Got a request, we dont want to process it
            # immedietely since other changes may be under way.
            
            # Another request coming in renews the initil request.
            # When there are no more requests, we go ahead and process
            # the event.
            if not self.regenerate_request.isSet() and pending:
                pending = False
                self.process_all()
            elif self.regenerate_request.isSet():
                pending = True
                self.regenerate_request.clear()


    def watch(self):
        while True:
            pending = self.queue.get()
            self.queue.task_done()
            if pending.setdefault("exception", False):
                raise
            resource = pending['resource']

            if resource.is_layout:
                self.regenerate_request.set()
                continue
            if self.process(resource, pending['change']):
                self.post_process(resource.node)
                self.siteinfo.target_folder.copy_contents_of(
                    self.siteinfo.temp_folder, incremental=True)
                

    def generate(self, deploy_path, keep_watching=False):
        setup_env(self.site_path)
        self.build_siteinfo(deploy_path)
        self.process_all()
        self.siteinfo.temp_folder.delete()
        if keep_watching:
           self.siteinfo.temp_folder.make()
           self.queue = Queue()
           self.watcher = Thread(target=self.watch)
           self.watcher.start()
           self.regenerator = Thread(target=self.regenerator)
           self.regenerator.start()
           self.siteinfo.monitor(self.queue)
           self.watcher.join()
    
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