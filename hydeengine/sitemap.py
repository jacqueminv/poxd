from django.conf import settings
from file_system import File, Folder

class SitemapNode(object):
    def __init__(self, parent, folder, name=None):
        super(SitemapNode, self).__init__()
        self.folder = folder
        self.parent = parent
        self.pages = []
        self.children = []
        self.listing_page = None
        if not name:
            self.name = folder.name
        else:
            self.name = name
        
    def __repr__(self):
        return self.folder.path
    
    def get_parent_of(self, folder):
        if folder.parent.path == self.folder.path:
            return self;
        current = self    
        if not current.isroot:
            current = self.parent
            return current.get_parent_of(folder)
        return None
    
    @property
    def has_listing(self):
        return not self.listing_page is None
    
    @property
    def listing_url(self):
        return self.listing_page.url
    
    @property
    def url(self):
        if settings.GENERATE_ABSOLUTE_FS_URLS:
            return self.folder.get_mirror_folder(settings.CONTENT_DIR, settings.DEPLOY_DIR, ignore_root=True).path
        else:
            return "/" + self.folder.get_fragment(settings.CONTENT_DIR)
    
    @property
    def isroot(self):
        return self.parent is None
        
    @property 
    def isleaf(self):
        return not self.children
        
    @property
    def siblings(self):
        if self.isroot: return None
        siblings = []
        siblings = self.parent.children[:]
        siblings.remove(self)
        return siblings
        
    @property
    def next_siblings(self):
        if not self.parent: return None
        siblings = self.parent.children
        index = siblings.index(self)
        return siblings[index+1:]
        
    @property
    def next_sibling(self):
        sibs = self.next_siblings
        if sibs:
            return sibs[0]
        return None
        
    @property
    def prev_siblings(self):
        if not self.parent: return None
        siblings = self.parent.children
        index = siblings.index(self)
        return siblings[:index]

    @property
    def prev_sibling(self):
        sibs = self.prev_siblings
        if sibs:
            return sibs[0]
        return None
        
    def append_child(self, folder):
        node = SitemapNode(self, folder)
        self.children.append(node)
        return node
        
    def add_page(self, page):
        self.pages.append(page)
        if settings.GENERATE_ABSOLUTE_FS_URLS:
            url = Folder(self.url).child(page.name)
        else:
            url = self.url + "/" + page.name
        page.url = url
        page.node = self
        if page.name_without_extension == self.name:
            self.listing_page = page
        
    def walk(self):
        yield self
        for child in self.children:
                   for node in child.walk():
                       yield node

    def walk_pages(self):
        for node in self.walk():
            for page in node.pages:
                yield page
        