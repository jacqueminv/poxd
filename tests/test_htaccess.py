"""
Tests of .htaccess file generation. 

For now, this just checks whether the demo site's generated .htaccess file
matches a known good file.
"""

import os
import sys
from django.conf import settings

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(TEST_ROOT + "/..")
 
sys.path = [ROOT] + sys.path

from hydeengine.file_system import File, Folder
from hydeengine import Initializer, setup_env, Generator
from hydeengine.templatetags.hydetags import RenderHydeRewriteRulesNode
from hydeengine.renderer import build_sitemap

TEST_SITE = Folder(TEST_ROOT).child_folder("test_site")

def setup_module(module):
    Initializer(TEST_SITE.path).initialize(ROOT, template="default", force=True)
    setup_env(TEST_SITE.path)

def teardown_module(module):
    TEST_SITE.delete()

class TestHtaccess:
    def setup_class(self):
        settings.GENERATE_ABSOLUTE_FS_URLS = False
        settings.GENERATE_CLEAN_URLS = True
        settings.APPEND_SLASH = False # See Also: TestHtaccessAppendSlash
        settings.LISTING_PAGE_NAMES = ['listing']
        settings.SITE_WWW_URL = "http://www.example.com"
        build_sitemap()
        self.htaccess_generator = RenderHydeRewriteRulesNode()

    def test_redirect_old_urls_auto_listing_pages(self):
        # test with one name
        settings.LISTING_PAGE_NAMES = ['listing']
        expected = r"""
RewriteCond %{THE_REQUEST} \.html
RewriteRule ^(.*/?([^/]+))/\2\.html http://www.example.com/$1 [R=301]

RewriteCond %{THE_REQUEST} \.html
RewriteRule ^([^.]+)/(listing)\.html$ http://www.example.com/$1 [R=301]
    """
        actual = self.htaccess_generator.redirect_old_urls_rules() 
        assert actual.strip() == expected.strip()

        # test with multiple names
        settings.LISTING_PAGE_NAMES = ['listing', 'index', 'default']
        expected = r"""
RewriteCond %{THE_REQUEST} \.html
RewriteRule ^(.*/?([^/]+))/\2\.html http://www.example.com/$1 [R=301]

RewriteCond %{THE_REQUEST} \.html
RewriteRule ^([^.]+)/(listing|index|default)\.html$ http://www.example.com/$1 [R=301]
    """
        actual = self.htaccess_generator.redirect_old_urls_rules() 
        assert actual.strip() == expected.strip()

        # test with no names
        settings.LISTING_PAGE_NAMES = []
        expected = r"""
RewriteCond %{THE_REQUEST} \.html
RewriteRule ^(.*/?([^/]+))/\2\.html http://www.example.com/$1 [R=301]
"""
        actual = self.htaccess_generator.redirect_old_urls_rules() 
        assert actual.strip() == expected.strip() 
