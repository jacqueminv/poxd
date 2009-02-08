from hydeengine.file_system import File, Folder
from hydeengine import url

class SiteResource(object):
    def __init__(self, a_file, node):
        super(SiteResource, self).__init__()
        self.resource_file = a_file
        self.node = node
    
    @property
    def url(self):
        if not node.url:
            return None
        return url.join(node.url, self.resource_file.name)
    
    @property
    def full_url(self):
        if not node.full_url:
            return None
        return url.join(node.full_url, self.resource_file.name)
    
    @property
    def source_file(self):
        return self.file
    
    @property
    def target_file(self):
        return File(self.node.target_folder.child(self.file.name))
        
    @property
    def temp_file(self):
        return File(self.node.temp_folder.child(self.file.name))
        
    def __repr__(self):
        return str(self.resource_file)

class SiteNode(object):
    def __init__(self, folder, parent=None):
        super(SiteNode, self).__init__()
        self.folder = folder
        self.parent = parent
        self.site = self
        if self.parent:
            self.site = self.parent.site
        self.children = []
        self.resources = []
    
    def __repr__(self):
        return str(self.folder)
        
    @property
    def isroot(self):
        return not self.parent
        
    @property
    def name(self):
        return self.folder.name
        
    def walk(self):
        yield self
        for child in self.children:
            for node in child.walk():                
                yield node
    
    def find_child(self, folder):
        for node in self.walk():
            if node.folder.same_as(folder):
                return node
        return None
        
    def add_child(self, folder):
        if ContentNode.is_content(self.site, folder):
            node = ContentNode(folder, parent=self)
        elif LayoutNode.is_layout(self.site, folder):
            node = LayoutNode(folder, parent=self)
        elif MediaNode.is_media(self.site, folder):
            node = MediaNode(folder, parent=self)            
        else:
            node = SiteNode(folder, parent=self)    
        self.children.append(node)
        return node
        
    def add_resource(self, a_file):
        resource = SiteResource(a_file, self)
        self.resources.append(resource)
        return resource
        
    def find_node(self, folder):
        if self.folder.same_as(folder):
            return self
        found_node = None
        # Check parents first
        #
        if not self.isroot:
            found_node = self.parent.find_node(folder)
        # Check children
        #     
        if not found_node:
            found_node = self.find_child(folder)
        return found_node
    
    def find_resource(self, a_file):
        node = self.find_node(a_file.parent)
        if not node:
            return None
        for resource in node.resources:
            if resource.resource_file.same_as(a_file):
                return resource
        return None
    
    @property
    def source_folder(self):
        return self.folder

    @property
    def target_folder(self):
        return None
        
    @property
    def temp_folder(self):
        return None

    @property
    def url(self):
        return None    
        
    @property   
    def full_url(self):
        if not self.url:
            return None
        return url.join(self.site.settings.SITE_WWW_URL, self.url)
        
    @property
    def type(self):
        return None
        
class ContentNode(SiteNode):

    @staticmethod
    def is_content(site, folder):
        return (site.content_folder.same_as(folder) or
                site.content_folder.is_ancestor_of(folder))
    
    @property
    def target_folder(self):
        deploy_folder = self.site.target_folder
        return deploy_folder.child_folder_with_fragment(self.url)

    @property
    def temp_folder(self):
        temp_folder = self.site.temp_folder
        return temp_folder.child_folder_with_fragment(self.url)

    @property
    def url(self):
        return url.fixslash(
                self.folder.get_fragment(self.site.content_folder))
    
    @property            
    def type(self):
      return "content"
          
class LayoutNode(SiteNode):
    
    @staticmethod
    def is_layout(site, folder):
        return (site.layout_folder.same_as(folder) or
                site.layout_folder.is_ancestor_of(folder))
                
    @property
    def type(self):
        return "layout"          
          
class MediaNode(SiteNode):

    @staticmethod
    def is_media(site, folder):
        return (site.media_folder.same_as(folder) or
                site.media_folder.is_ancestor_of(folder))
    
    @property
    def url(self):
        return url.fixslash(
                self.folder.get_fragment(self.site.folder))

    @property            
    def type(self):
        return "media"    
        
    @property
    def target_folder(self):
        deploy_folder = self.site.target_folder
        return deploy_folder.child_folder_with_fragment(self.url)

    @property
    def temp_folder(self):
        temp_folder = self.site.temp_folder
        return temp_folder.child_folder_with_fragment(self.url)      
    
class SiteInfo(SiteNode):
    def __init__(self, settings, site_path, visitor=None):
        super(SiteInfo, self).__init__(Folder(site_path))
        self.settings = settings
        self.update(visitor)
     
    @property
    def content_folder(self):
        return Folder(self.settings.CONTENT_DIR)
    
    @property
    def layout_folder(self):
        return Folder(self.settings.LAYOUT_DIR)
        
    @property
    def media_folder(self):
        return Folder(self.settings.MEDIA_DIR)

    @property
    def temp_folder(self):
        return Folder(self.settings.TMP_DIR)

    @property
    def target_folder(self):
        return Folder(self.settings.DEPLOY_DIR)

        
    def update(self, visitor):
        class Visitor(object):
            def __init__(self, siteinfo):
                self.current_node = siteinfo
                
            def visit_file(self, a_file):
                resource = self.current_node.add_resource(a_file)
                try:
                    visitor.visit_resource(resource)
                except AttributeError:
                    pass
                    
            def visit_folder(self, folder):
                node = self.current_node.find_node(folder)
                if node:
                    self.current_node = node
                else:
                    parent = self.current_node.find_node(folder.parent)
                    self.current_node = parent.add_child(folder)
                try:
                    visitor.visit_node(self.current_node)
                except AttributeError:
                    pass
                    
            def visit_complete(self):
                try:
                    visitor.visit_complete()
                except AttributeError:
                    pass
                    
        self.folder.walk(visitor=Visitor(self))