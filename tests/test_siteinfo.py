import os
import sys
import unittest
from django.conf import settings


TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(TEST_ROOT + "/..")

sys.path = [ROOT] + sys.path

from hydeengine.file_system import File, Folder
from hydeengine import Initializer, setup_env
from hydeengine.siteinfo import SiteNode, SiteInfo

TEST_SITE = Folder(TEST_ROOT).child_folder("test_site")

def setup_module(module):
    Initializer(TEST_SITE.path).initialize(ROOT, force=True)
    setup_env(TEST_SITE.path)
    
def teardown_module(module):
    TEST_SITE.delete()

class TestSiteInfo:

    def setup_method(self, method):
        self.site = SiteInfo(settings, TEST_SITE.path)        

    def assert_node_complete(self, node, folder):
        assert node.folder.path == folder.path
        test_case = self
        class Visitor(object):
            def visit_folder(self, folder):
                child = node.find_child(folder)
                assert child
                test_case.assert_node_complete(child, folder)
                
            def visit_file(self, a_file):
                assert node.find_resource(a_file)
                
        folder.list(Visitor())

    def test_population(self):
        assert self.site.name == "test_site"
        self.assert_node_complete(self.site, TEST_SITE)
        
    def test_type(self):
        def assert_node_type(node_dir, type):
           node = self.site.find_child(Folder(node_dir))
           assert node
           assert Folder(node_dir).same_as(node.folder)
           for child in node.walk():
               assert child.type == type
        assert_node_type(settings.CONTENT_DIR, "content")
        assert_node_type(settings.MEDIA_DIR, "media")
        assert_node_type(settings.LAYOUT_DIR, "layout")
        
    def test_urls(self):
        for node in self.site.walk():
            if node.type == "content":
                fragment = node.folder.get_fragment(self.site.content_folder)
                assert node.url == fragment
                assert node.full_url == settings.SITE_WWW_URL + "/" + fragment
            elif node.type == "media":
                assert node.url == node.folder.get_fragment(self.site.folder)
            else:
                assert not node.url
                
    def test_folders(self):
        for node in self.site.walk():
            fragment = ''
            if node.type == "content":
                fragment = node.folder.get_fragment(self.site.content_folder)
            elif node.type == "media":
                fragment = node.folder.get_fragment(self.site.folder)
             
            assert node.source_folder == node.folder
            if not node == self.site and node.type not in ("content", "media"):
                assert not node.target_folder
                assert not node.temp_folder
            else:     
                assert node.target_folder.same_as(Folder(
                                os.path.join(settings.DEPLOY_DIR, fragment)))
                assert node.temp_folder.same_as(Folder(
                           os.path.join(settings.TMP_DIR, fragment)))
                           
    def                        