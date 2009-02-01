from django.conf import settings
from file_system import File
from datetime import datetime
from hydeengine.templatetags.hydetags import xmldatetime
import commands

class FolderFlattener:
    
    @staticmethod
    def process(folder, params):
        class Flattener:
            def __init__(self, folder, params):
                self.folder = folder
                self.remove_processed_folders = \
                 params["remove_processed_folders"]
                self.previous_folder = None
            
            def visit_file(self, file):
                if not self.folder.is_parent_of(file):
                    file.copy_to(self.folder)
                
            def visit_folder(self, this_folder):                
                if self.previous_folder and self.remove_processed_folders:
                    self.previous_folder.delete()
                if not self.folder.same_as(this_folder):
                    self.previous_folder = this_folder
                    
            def visit_complete(self):
                if self.previous_folder and self.remove_processed_folders:
                    self.previous_folder.delete()

        folder.walk(Flattener(folder, params), params["pattern"])


SITEMAP_CONFIG = \
"""<?xml version="1.0" encoding="UTF-8"?>
<site
  base_url="%(base_url)s"
  store_into="%(sitemap_path)s"
  suppress_search_engine_notify="1"
  verbose="1"
  >
  <urllist  path="%(url_list_file)s"/>
</site>"""

class GoogleSitemapGenerator:
    
    @staticmethod
    def process(folder, params):
        site = settings.CONTEXT['site']
        url_list_file = params["url_list_file"] 
        urllist = open(url_list_file, 'w')
        for page in site.walk_pages():
            if not page.kind == "html":
                continue
            created = (page.created,  datetime.strptime(
                "2000-01-01 00:00", settings.DATETIME_FORMAT))[not page.created]
            if not hasattr(page, "updated"):
                updated = created
            else:
                updated = (page.updated, page.created)[not page.updated]
            created = xmldatetime(created)
            updated = xmldatetime(updated)
            url = page.full_url
            priority = 0.5
            if page.listing:
                priority = 1.0
            changefreq = "weekly"
            urllist.write(
                "%(url)s lastmod=%(updated)s changefreq=%(changefreq)s \
priority=%(priority).1f\n" 
                % locals())
        urllist.close()
        base_url = settings.SITE_WWW_URL
        sitemap_path = params["sitemap_file"]
        config_file =  params["config_file"]
        config = open(config_file, 'w')
        config.write(SITEMAP_CONFIG % locals())        
        config.close()
        generator = params["generator"]
        command = u"python %s --config=%s" % (generator, config_file)
        status, output = commands.getstatusoutput(command)
        print command  
        print output      
        if status > 0: 
            print output