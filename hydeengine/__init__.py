import imp
import sys
import os
import shutil
import threading

from collections import defaultdict
from datetime import datetime
from threading import Thread, Event
from Queue import Queue

from django.conf import settings
from django.core.management import setup_environ
from django.template import add_to_builtins
from django.template.loader import render_to_string

from path_util import PathUtil
from file_system import File, Folder
from processor import Processor
from siteinfo import SiteInfo

class hyde_defaults:
    
    GENERATE_CLEAN_URLS = True
    GENERATE_ABSOLUTE_FS_URLS = False
    LISTING_PAGE_NAMES = ['index', 'default', 'listing']
    APPEND_SLASH = False
    MEDIA_PROCESSORS = {}
    CONTENT_PROCESSORS = {}
    SITE_POST_PROCESSORS = {} 
    CONTEXT = {}
    
def setup_env(site_path):
    """
    
    Initializes Django Environment
    
    """
    # Don't do it twice
    if hasattr(settings, "CONTEXT"):
        return
    try:
       hyde_site_settings = imp.load_source("hyde_site_settings",
                        os.path.join(site_path,"settings.py"))
    except SyntaxError, err:
        print "The given site_path [%s] contains a settings file " \
              "that could not be loaded due syntax errors." % site_path
        print err
        exit()
    except Exception, err:
        print "Cannot Import Site Settings"
        print err
        raise ValueError(
        "The given site_path [%s] does not contain a hyde site. "
        "Give a valid path or run -init to create a new site."
        %  site_path
        )
        
    try:
        from django.conf import global_settings
        defaults = global_settings.__dict__
        defaults.update(hyde_site_settings.__dict__)
        settings.configure(hyde_defaults, **defaults)
    except Exception, err:
        print "Site settings are not defined properly"
        print err
        raise ValueError(
        "The given site_path [%s] has invalid settings. "
        "Give a valid path or run -init to create a new site."
        %  site_path
        )

def validate_settings(settings):
    if settings.GENERATE_CLEAN_URLS and settings.GENERATE_ABSOLUTE_FS_URLS:
        raise ValueError(
        "GENERATE_CLEAN_URLS and GENERATE_ABSOLUTE_FS_URLS cannot "
        "be enabled at the same time."
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
        validate_settings(settings)
        deploy_folder = Folder(
                            (deploy_path, settings.DEPLOY_DIR)
                            [not deploy_path])
        if not 'site' in settings.CONTEXT:
            generator = Generator(server.site_path)
            generator.create_siteinfo()
        site = settings.CONTEXT['site']
        url_file_mapping = defaultdict(bool)
        # This following bit is for supporting listing pages with arbitrary
        # filenames.
        if settings.GENERATE_CLEAN_URLS:
            for page in site.walk_pages(): # build url to file mapping
                if page.listing and page.name_without_extension not in \
                   (settings.LISTING_PAGE_NAMES + [page.node.name]):
                    filename = os.path.join(settings.DEPLOY_DIR, page.name)
                    url = page.url.strip('/')
                    url_file_mapping[url] = filename

        import cherrypy
        from cherrypy.lib.static import serve_file
        server = self
        class WebRoot:
            @cherrypy.expose
            def index(self):
                page =  site.listing_page
                return serve_file(deploy_folder.child(page.name))
                
            if settings.GENERATE_CLEAN_URLS:
                @cherrypy.expose
                def default(self, *args):
                   # first, see if the url is in the url_file_mapping
                   # dictionary
                   file = url_file_mapping[os.sep.join(args)]
                   if file:
                       return serve_file(file)
                   # next, try to find a listing page whose filename is the
                   # same as its enclosing folder's name
                   file = os.path.join(deploy_folder.path, os.sep.join(args),
                       args[-1] + '.html') 
                   if os.path.isfile(file):
                       return serve_file(file)
                   # try each filename in LISTING_PAGE_NAMES setting
                   for listing_name in settings.LISTING_PAGE_NAMES:
                       file = os.path.join(deploy_folder.path, os.sep.join(args),
                           listing_name + '.html') 
                       if os.path.isfile(file):
                           return serve_file(file)
                   # failing that, search for a non-listing page
                   file = os.path.join(deploy_folder.path, os.sep.join(args[:-1]),
                       args[-1] + '.html') 
                   if os.path.isfile(file):
                       return serve_file(file)
                   # failing that, page not found
                   raise cherrypy.NotFound
            
        cherrypy.config.update({'environment': 'production',
                                  'log.error_file': 'site.log',
                                  'log.screen': True})
                                  
        # even if we're still using clean urls, we still need to serve media.
        if settings.GENERATE_CLEAN_URLS:
            conf = {'/media': {
            'tools.staticdir.dir':os.path.join(deploy_folder.path, 'media'), 
            'tools.staticdir.on':True
            }}
        else:
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
        self.regeneration_complete = Event()    
        self.processor = Processor(settings)
        threading.stack_size(1<<19)
    
    def process(self, resource, change="Added"):
        settings.CONTEXT['node'] = resource.node
        settings.CONTEXT['resource'] = resource
        return self.processor.process(resource)
        
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
        if not deploy_folder.exists:
            deploy_folder.make()
        add_to_builtins('hydeengine.templatetags.hydetags')
        add_to_builtins('hydeengine.templatetags.aym')
        add_to_builtins('hydeengine.templatetags.typogrify')
        self.create_siteinfo()
    
    def create_siteinfo(self):
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
                self.regeneration_complete.set()
            elif self.regenerate_request.isSet():
                self.regeneration_complete.clear()
                pending = True
                self.regenerate_request.clear()


    def watch(self):
        regenerating = False
        while True:
            pending = self.queue.get()
            self.queue.task_done()
            if pending.setdefault("exception", False):
                raise
            resource = pending['resource']

            if self.regeneration_complete.isSet():
                regenerating = False
                
            if resource.is_layout or regenerating:
                regenerating = True
                self.regenerate_request.set()
                continue
                    
            if self.process(resource, pending['change']):
                self.post_process(resource.node)
                self.siteinfo.target_folder.copy_contents_of(
                    self.siteinfo.temp_folder, incremental=True)                

    def generate(self, deploy_path=None, keep_watching=False):
        setup_env(self.site_path)
        validate_settings(settings)
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
           self.regenerator.join()
    
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