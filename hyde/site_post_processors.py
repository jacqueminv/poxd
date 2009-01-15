from django.conf import settings
from file_system import *
from folders import *
from renderer import render_page

class IndexProcessor:
 
    @staticmethod
    def process(sitmap):
        default_template = File(Folder(settings.SITE_TEMPLATE_DIR).child('listing.html'))                
        class Indexer:

            def visit_folder(self, folder):
                if folder.
                try:
                    template = File(settings.LISTING_TEMPLATES[folder.get_fragment(settings.CONTENT_DIR)])
                except:
                    template = default_template
                
                
        
        while true
        
        for folder in content:
            default_template = File(Folder(settings.SITE_TEMPLATE_DIR).child('listing.html'))
            try:
                template = File(settings.LISTING_TEMPLATES[folder.get_fragment(settings.CONTENT_DIR)])
            except:
                template = default_template
            mirror = folder.get_mirror_folder(settings.CONTENT_DIR, settings.TMP_DIR, ignore_root=True) 
            new_page = template.copy_to(mirror)
            content_folder = ContentFolder()
            content_folder.visit_folder(None, new_page.parent)
            content_folder.process_file(new_page)
            settings.CONTEXT['folder'] = folder
            render_page(new_page)