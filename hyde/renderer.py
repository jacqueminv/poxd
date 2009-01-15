from django.conf import settings
from django.template.loader import render_to_string
from django.template import add_to_builtins
from file_system import *
from folders import *
from sitemap import *

def get_page_url(page):
    if settings.GENERATE_ABSOLUTE_FS_URLS:
        mirror = page.parent.get_mirror_folder(settings.CONTENT_DIR, settings.DEPLOY_DIR, ignore_root=True)
        page_url = mirror.child(page.name)
    else:
        fragment = page.parent.get_fragment(settings.CONTENT_DIR)
        page_url = os.sep + fragment + page.name
    return page_url

def render_pages():
    class Renderer(object):
        sitemap = None
        current_node = None
        
        def visit_folder(self, folder):
            if not self.sitemap:
                self.sitemap = SitemapFolder(None, folder)
                self.current_node = self.sitemap
            else:
                parent = self.current_node.get_parent_of(folder)
                if parent:
                   self.current_node = parent.append_child(folder)
            
        def add_page(self, page, context):
            self.current_node.pages.append(page)
            page.context =  context
            page.sitemap = self.current_node
            
        def visit_file(self, file):
            render_page(file)
            self.add_page(file, settings.CONTEXT['page'])
            
    renderer = Renderer()
    ContentFolder().walk(renderer)
    return renderer.sitemap

def post_process_site(sitemap):
    for processor_name in settings.SITE_POST_PROCESSORS:
        processor = load_processor(processor_name)
        processor.process(sitemap)
            
def render_page(page):
    rendered = render_to_string(str(page), settings.CONTEXT)    
    mirror = page.parent.get_mirror_folder(settings.CONTENT_DIR, settings.TMP_DIR, ignore_root=True)
    page.write(rendered)