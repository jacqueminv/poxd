"""

uses py.test

sudo easy_install py

http://codespeak.net/py/dist/test.html

"""
import os
import sys
import unittest
from threading import Thread
from Queue import Queue
from Queue import Empty

from django.conf import settings

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(TEST_ROOT + "/..")

sys.path = [ROOT] + sys.path

from hydeengine.file_system import File, Folder
from hydeengine import url
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
        
    def test_attributes(self):
        for node in self.site.walk():
           self.assert_node_attributes(node)
           for resource in node.resources:
               self.assert_resource_attributes(resource)
                           
    def assert_node_attributes(self, node):
        fragment = self.get_node_fragment(node)
        if node.type == "content":
            fragment = node.folder.get_fragment(self.site.content_folder)
        elif node.type == "media":
            fragment = node.folder.get_fragment(self.site.folder)
            
        if node.type in ("content", "media"):
            fragment = "/" + fragment.lstrip("/").rstrip("/")
            assert node.url == fragment
            assert node.full_url == settings.SITE_WWW_URL + fragment
        else:    
            assert not node.url
            assert not node.full_url
                
        assert node.source_folder == node.folder
        if not node == self.site and node.type not in ("content", "media"):
            assert not node.target_folder
            assert not node.temp_folder
        else:
            assert node.target_folder.same_as(Folder(
                            os.path.join(settings.DEPLOY_DIR,
                                fragment.lstrip("/"))))
            assert node.temp_folder.same_as(Folder(
                            os.path.join(settings.TMP_DIR, 
                                fragment.lstrip("/"))))
                       
    def assert_resource_attributes(self, resource):
        node = resource.node
        fragment = self.get_node_fragment(node)
        if resource.node.type in ("content", "media"):
            assert (resource.url ==  
                        url.join(node.url, resource.resource_file.name))
            assert (resource.full_url ==  
                        url.join(node.full_url, resource.resource_file.name))
            assert resource.target_file.same_as(
                    File(node.target_folder.child(
                            resource.resource_file.name)))
            assert resource.temp_file.same_as(
                    File(node.temp_folder.child(resource.resource_file.name)))
        else:
            assert not resource.url
            assert not resource.full_url
        
        assert resource.source_file.parent.same_as(node.folder)
        assert resource.source_file.name == resource.resource_file.name
        
    def get_node_fragment(self, node):
        fragment = ''
        if node.type == "content":
            fragment = node.folder.get_fragment(self.site.content_folder)
        elif node.type == "media":
            fragment = node.folder.get_fragment(self.site.folder)
        return fragment
        
class TestSiteInfoContinuous:
    
    def setup_method(self, method):
        self.site = SiteInfo(settings, TEST_SITE.path)
        self.exception_queue = Queue()
        
    def change_checker(self, change, path):
        try:
            changes = self.site.queue.get(block=True, timeout=5)
            assert changes
            assert not changes['exception']
            assert changes['change'] == change
            assert changes['resource']
            assert changes['resource'].resource_file.path == path
        except:
            self.exception_queue.put(sys.exc_info())
            raise
            
    def test_monitor_stop(self):
        m = self.site.monitor()
        self.site.dont_monitor()
        assert not m.isAlive()
            
    def test_modify(self):
        self.site.monitor()
        path = self.site.media_folder.child("css/base.css")
        t = Thread(target=self.change_checker, 
                    kwargs={"change":"Modified", "path":path})
        t.start()
        os.utime(path, None)
        t.join()
        assert self.exception_queue.empty()
            
        
    def test_add(self, direct=False):
        self.site.monitor()
        path = self.site.layout_folder.child("test.ggg")
        t = Thread(target=self.change_checker, 
                    kwargs={"change":"Added", "path":path})
        t.start()      
        f = File(path)        
        f.write("test")
        t.join()
        if not direct:
            f.delete()
        assert self.exception_queue.empty()        
        
    def test_delete(self):
        path = self.site.layout_folder.child("test.ggg")
        self.test_add(direct=True)
        t = Thread(target=self.change_checker, 
                    kwargs={"change":"Deleted", "path":path})
        t.start()      
        File(path).delete()
        t.join()
        assert self.exception_queue.empty()
        
    def test_stop_monitor(self):
        self.site.dont_monitor()
