import os
import sys
import unittest

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(TEST_ROOT + "/..")

sys.path = [ROOT] + sys.path

from hydeengine.file_system import File, Folder
from hydeengine import Initializer, setup_env
from hydeengine.siteinfo import SiteNode, SiteInfo

TEST_SITE = Folder(TEST_ROOT).child_folder("test_site")

def setup_tests():
    Initializer(TEST_SITE.path).initialize(ROOT, force=True)
    setup_env(TEST_SITE.path)
    
def teardown_tets():
    TEST_SITE.delete()

class TestSiteInfo(unittest.TestCase):

    def testCanReadSiteInfoContent(self):
        site = SiteInfo(TEST_SITE)
        self.assertEqual(site.name, "test_site")
        
if __name__ == '__main__':
    setup_tests()
    unittest.main()
    teardown_tests()