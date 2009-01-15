class SitemapFolder(object):
    def __init__(self, parent, folder, children = [], pages = []):
        super(SitemapFolder, self).__init__()
        self.folder = folder
        self.children = children
        self.pages = pages
        self.parent = parent

    
    def get_parent_of(self, folder):
        if folder.parent.path == self.folder.path:
            return self;
        current = self    
        if not current.isroot:
            current = self.parent
            return current.get_parent_of(folder)
        return None
        
    
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
        return next_siblings[0]
        
    @property
    def prev_siblings(self):
        if not self.parent: return None
        siblings = self.parent.children
        index = siblings.index(self)
        nextsiblings = siblings[:index]

    @property
    def prev_sibling(self):
        return prev_siblings[0]    
        
    def append_child(folder, children = [], pages = []):
        node = SitemapFolder(self, folder, children, pages)
        self.children.append(node)
        return node
        
    def walk(self, visitor):
        visitor.visit_folder(self.folder)
        for page in self.pages:
            visitor.visit_page(page)
        for child in self.children:
            child.walk(visitor)
        