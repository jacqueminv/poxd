import os
import string
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
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
        sitemap_path = params["sitemap_file"]
        url_list_file = File(sitemap_path).parent.child("urllist.txt")
        config_file =  File(sitemap_path).parent.child("sitemap_config.xml")
        urllist = open(url_list_file, 'w')
        for page in site.walk_pages():
            if not page.kind == "html" or page.exclude:
                continue
            created = xmldatetime(page.created)
            updated = xmldatetime(page.updated)
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
        config = open(config_file, 'w')
        config.write(SITEMAP_CONFIG % locals())        
        config.close()
        generator = params["generator"]
        command = u"python %s --config=%s" % (generator, config_file)
        status, output = commands.getstatusoutput(command)
        if status > 0: 
            print output
        File(config_file).delete()
        File(url_list_file).delete()


REWRITE_RULES = string.Template( \
r"""
####  BEGIN HYDE CLEAN URL REWRITE RULES.  ####

# 301 redirect requests to the .html files to the clean urls
${redirect_old_urls_rules}

# lising pages defined by LISTING_PAGE_NAMES
${auto_rules}

# listing pages whose names are the same as their enclosing folder's
RewriteCond %{REQUEST_FILENAME}/$1.html -f 
RewriteRule ^([^/]*)/$ %{REQUEST_FILENAME}/$1.html

# listing pages with 'listing: true' attribute manually set
${manual_rules}

# regular pages
RewriteCond %{REQUEST_FILENAME}.html -f
RewriteRule ^.*$ %{REQUEST_FILENAME}.html

####  END HYDE CLEAN URL REWRITE RULES.  ####
""")

AUTO_REWRITE_RULE = string.Template(\
r"""
RewriteCond %{REQUEST_FILENAME}/${name}.html -f
RewriteRule ^(.*) $1/${name}.html
"""
)

REDIRECT_OLD_URLS_RULE = string.Template(\
r"""
RewriteCond %{THE_REQUEST} \.html
RewriteRule ^(.*/?([^/]+))/\2\.html ${site_url}/$1${trailing_slash} [R=301]

RewriteCond %{THE_REQUEST} \.html
RewriteRule ^([^.]+)/(${lpn_names})\.html$ ${site_url}/$1${trailing_slash} [R=301]
"""
)

class HtaccessGenerator:
    """Generates a .htaccess file and places it in the root of the deploy
    directory.  
    
    The template for the .htaccess file is specified using the
    template parameter.  A context variable, HYDE_REWRITE_RULES, contains the
    Mod_Rewrite RewriteRules for serving content with clean urls.  If the
    GENERATE_CLEAN_URLS setting is disabled, HYDE_REWRITE_RULES will be empty.

    HYDE_REWRITE_RULES does not enable the RewriteEngine or set the
    RewriteBase; it only contains RewriteRules.
    """

    @staticmethod
    def process(folder, params):
        site = settings.CONTEXT['site']
        htaccess_file = os.path.join(settings.TMP_DIR, '.htaccess')
        htaccess_template = params['template']
        context = {}
        if settings.GENERATE_CLEAN_URLS:
            # generate the rules to redirect requests to html files to clean
            # urls
            if settings.APPEND_SLASH:
                trailing_slash = '/'
            else:
                trailing_slash = ''
            redirect_old_urls_rules = REDIRECT_OLD_URLS_RULE.safe_substitute( \
                {'site_url': settings.SITE_WWW_URL.rstrip('/'),
                 'lpn_names': '|'.join(settings.LISTING_PAGE_NAMES),
                 'trailing_slash' : trailing_slash
                })
            # generate the rules to map clean urls to html files
            auto_rules = [] # for LISTING_PAGE_NAMES listings
            for name in settings.LISTING_PAGE_NAMES:
                auto_rules.append(AUTO_REWRITE_RULE.safe_substitute( \
                    {'name': name}))
            manual_rules_url_map = [] # for 'listing: true' listings
            for page in site.walk_pages(): # build url to file mapping
                if page.listing and page.name_without_extension not in \
                   (settings.LISTING_PAGE_NAMES + [page.node.name]):
                    filename = os.path.join(page.url, page.name)
                    if settings.APPEND_SLASH:
                        url = page.url.lstrip('/')
                    else:
                        url = page.url.strip('/')
                    manual_rules_url_map.append((url, filename))
            manual_rules = []
            for page in manual_rules_url_map: # turn that mapping into RewriteRules
                manual_rules.append("RewriteRule ^%s$ %s\n" % page)
            context['HYDE_REWRITE_RULES'] = mark_safe(REWRITE_RULES.safe_substitute( \
                {'auto_rules' : ''.join(auto_rules),
                 'manual_rules' : ''.join(manual_rules),
                 'redirect_old_urls_rules' : redirect_old_urls_rules
                }))
        else:
            context['HYDE_REWRITE_RULES'] = ''
        htaccess = open(htaccess_file, 'w')
        htaccess.write(render_to_string(htaccess_template, 
            dict(context.items() + settings.CONTEXT.items())))
        htaccess.close()
