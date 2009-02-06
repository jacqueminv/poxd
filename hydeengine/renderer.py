import os
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from folders import ContentFolder
from sitemap import SitemapNode

def build_sitemap():
    class Builder(object):
        site = None
        current_node = None
        
        def visit_folder(self, folder):
            if not self.site:
                self.site = SitemapNode(None, folder, settings.SITE_NAME)
                self.current_node = self.site
                settings.CONTEXT['site'] = self.site
            else:
                parent = self.current_node.get_parent_of(folder)
                if parent:
                    self.current_node = parent.append_child(folder)
                    
        def visit_file(self, page):  
            self.current_node.add_page(page)
            
    builder = Builder()        
    ContentFolder().walk(builder, "[!_]*")
    builder.site.sort_and_link_pages()

def render_pages(basetime=None):
    if not basetime:
        basetime = datetime.strptime("2000-01-01", "%Y-%m-%d")
    for page in settings.CONTEXT['site'].walk_pages():
        # TODO: This is still incomplete.
        # Pages thate contain , excerpts, listing pages, latest excerpts
        # have to be handled separately
        #
        source_file = page.source_file
        if not page.exists or source_file.changed_since(basetime):
            settings.CONTEXT['page'] = page
            render_page(page)
            
def render_page(page):
    print "Rendering " + str(page)
    rendered = render_to_string(str(page), settings.CONTEXT)    
    page.write(rendered)
