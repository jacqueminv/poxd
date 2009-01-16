from django.conf import settings
from file_system import File, Folder

class SitemapNode(object):
    def __init__(self, parent, folder):
        super(SitemapNode, self).__init__()
        self.folder = folder
        self.parent = parent
        self.pages = []
        self.children = []
        
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
    def name(self):
        return self.folder.name
    
    @property
    def url(self):
        if settings.GENERATE_ABSOLUTE_FS_URLS:
            return Folder(settings.DEPLOY_DIR).child(self.name)
        else:
            return "/" + self.name
    
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
        page.node = self
        
    def walk(self):
        yield self
        for child in self.children:
                   for node in child.walk():
                       yield node

    def walk_pages(self):
        for node in self.walk():
            for page in node.pages:
                yield page
        