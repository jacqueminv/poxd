import imp, sys, os, shutil
from django.conf import settings
from django.core.management import setup_environ
from path_util import PathUtil
from django.template.loader import render_to_string
from django.template import add_to_builtins
from file_system import *
from folders import *

def load_processor(name):
    (module_name, dot, processor) = name.rpartition(".")
    __import__(module_name)
    module = sys.modules[module_name]
    return getattr(module, processor)

class Generator(object):
    def __init__(self, site_path):
        super(Generator, self).__init__()
        self.site_path = os.path.abspath(os.path.expandvars(os.path.expanduser(site_path)))
    
    def generate(self, deploy_path):
        try:
            imp.load_source("hyde_site_settings", os.path.join(self.site_path,"settings.py"))
        except Exception, e:
            print "Cannot Import Site Settings"
            raise ValueError("The given site_path [%s] does not contain a hyde site. Give a valid path or run -init to create a new site." % self.site_path)
            
        try:
            os.environ['DJANGO_SETTINGS_MODULE'] = u"hyde_site_settings"
        except Exception, e:
            print "Site settings are not defined properly"
            raise ValueError("The given site_path [%s] does not contain a hyde site. Give a valid path or run -init to create a new site." % self.site_path)
        
        tmp_folder = Folder(settings.TMP_DIR)
        backup_folder = Folder(settings.BACKUPS_DIR).make()
        deploy_folder = Folder((deploy_path, settings.DEPLOY_DIR)[not deploy_path])
        media_folder = Folder(settings.MEDIA_DIR)
        
        if(deploy_folder.exists):
            deploy_folder.backup(backup_folder)

        tmp_folder.delete()
        tmp_folder.make()

        if settings.GENERATE_ABSOLUTE_FS_URLS:
            media_root = tmp_folder.child(media_folder.name)
        else:
            media_root = os.sep + media_folder.name
            
        settings.CONTEXT['media'] = media_root
        MediaFolder().walk()    
        self.render_pages()
        deploy_folder.make()
        deploy_folder.move_contents_of(tmp_folder)
        tmp_folder.delete()
    
    def render_pages(self):
        add_to_builtins('hyde.templatetags.hydetags')
        add_to_builtins('hyde.templatetags.aym')
        context = settings.CONTEXT
        out_dir = settings.TMP_DIR
        
        class ListingVisitor:
            def __init__(self):
               self.subfolders = []
            
            def visit_folder(self, folder):
                self.subfolders.append({"name": os.path.basename(folder),           "pages": []})

            def visit_page(self, page_path, page_context):
                top = self.subfolders[len(self.subfolders)-1]
                if page_context.has_key('listing_needed'):
                    top['url'] = page_context['page_url']
                    return
                top['pages'].append(page_context)
        
        class PageVisitor:
            @staticmethod
            def visit_folder(folder):pass
            @staticmethod
            def visit_page(page_path, page_context):
                if page_context.has_key('listing_needed'):
                    if page_context['listing_needed']:
                        listing_visitor = ListingVisitor()
                        ContentWalker.walk(os.path.dirname(page_path), listing_visitor)
                        page_context['subfolders'] = listing_visitor.subfolders
                context['page'] = page_context
                rendered = render_to_string(page_path,context)
                source_dir = os.path.dirname(page_path)
                page_out_dir = PathUtil.mirror_dir_tree(source_dir, settings.CONTENT_DIR, out_dir, ignore_root=True)
                page_path = os.path.join(page_out_dir,os.path.basename(page_path))
                fout = open(page_path,'w')
                fout.write(rendered)
                fout.close()

        ContentWalker.walk(settings.CONTENT_DIR, PageVisitor)
    
context_cache = {}              
                
class ContentWalker(object):
    @staticmethod
    def walk(walk_dir, visitor):
        default_processor = settings.CONTENT_PROCESSORS['*']
        for root, dirs, files in os.walk(walk_dir):
            PathUtil.filter_hidden_inplace(dirs)
            PathUtil.filter_hidden_inplace(files)
            visitor.visit_folder(root)
            processor = default_processor
            fragment = PathUtil.get_path_fragment(settings.CONTENT_DIR, root)
            if len(fragment) and settings.CONTENT_PROCESSORS.has_key(fragment):
                processor = settings.CONTENT_PROCESSORS[fragment]
                if not processor:
                    processor = "hyde.content_processors.YAMLContentProcessor"
            processor = load_processor(processor)
            for page in files:
                if page.startswith("_"): continue
                page_path = os.path.join(root, page)
                if not context_cache.has_key(page_path):
                    
                    page_context = processor.get_page_context(page_path)
                    if settings.GENERATE_ABSOLUTE_FS_URLS:
                        page_out_dir = PathUtil.mirror_dir_tree(os.path.dirname(page_path), settings.CONTENT_DIR, settings.TMP_DIR, ignore_root=True)
                        page_url = os.path.join(page_out_dir,os.path.basename(page_path))
                    else:
                        fragment = PathUtil.get_path_fragment(settings.CONTENT_DIR, root)
                        page_url = os.sep + fragment + page
                    page_context['page_url'] = page_url
                    context_cache[page_path] = page_context
                else:
                    page_context = context_cache[page_path]
                visitor.visit_page(page_path, page_context)
    
class Initializer(object):
    def __init__(self, site_path):
        super(Initializer, self).__init__()
        self.site_path = os.path.abspath(os.path.expandvars(os.path.expanduser(site_path)))

    def initialize(self, root, template):
        if not template:
            template = "default"
        template_dir = os.path.join(root, "site_templates", template)
        if not os.path.exists(template_dir):
            raise ValueError("Cannot find the specified template[%s]." % template_dir)
            
        if not os.path.exists(self.site_path):
            os.makedirs(self.site_path)
        else:
            files = os.listdir(self.site_path)
            PathUtil.filter_hidden_inplace(files)
            if len(files):
                raise ValueError("The site_path[%s] is not empty." % self.site_path)
            
        files = os.listdir(template_dir)
        for file in files:
            source = os.path.join(template_dir, file)
            dest = os.path.join(self.site_path, file)
            if os.path.isdir(source):
                shutil.copytree(source, dest)
            else:
                shutil.copy(source, dest)