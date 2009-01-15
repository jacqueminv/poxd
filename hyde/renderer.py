from django.conf import settings
from django.template.loader import render_to_string
from django.template import add_to_builtins
from file_system import *
from folders import *

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
        content = None
        
        def visit_folder(self, folder):
            if not self.content:
                self.content = []
            else:
                    
            folder.pages = []
            self.content.append(folder)
        
        def add_folder(self, page):
            top = self.content[len(self.content)-1]
            top.pages.append(page)
            page.context =  context
            
        def add_page(self, page, context):
            top = self.content[len(self.content)-1]
            top.pages.append(page)
            page.context =  context
            
        def visit_file(self, file):
            render_page(file)
            self.add_page(file, settings.CONTEXT['page'])
            
    renderer = Renderer()
    ContentFolder().walk(renderer)
    return renderer.content

def post_process_site(content):
    for processor_name in settings.SITE_POST_PROCESSORS:
        processor = load_processor(processor_name)
        processor.process(content)
            
def render_page(page):
    rendered = render_to_string(str(page), settings.CONTEXT)    
    mirror = page.parent.get_mirror_folder(settings.CONTENT_DIR, settings.TMP_DIR, ignore_root=True)
    page.write(rendered)