import sys
import re
from threading import Thread, Event
import time


from hydeengine.file_system import File, Folder
from hydeengine import url

class SiteResource(object):
    def __init__(self, a_file, node):
        super(SiteResource, self).__init__()
        self.node = node
        self.file = a_file
        self.source_file = self.file
        if self.node.target_folder:
            self.target_file = File(
                        self.node.target_folder.child(self.file.name))
            self.temp_file = File(
                        self.node.temp_folder.child(self.file.name))
        self.last_known_modification_time = a_file.last_modified
    
    @property
    def has_changes(self):
        return (not self.last_known_modification_time ==
                    self.file.last_modified)
    
    @property
    def url(self):
        if self.node.url is None:
            return None
        return url.join(self.node.url, self.file.name)
        
    @property
    def last_modified(self):
        return self.file.last_modified
    
    @property
    def full_url(self):
        if not self.node.full_url:
            return None
        return url.join(self.node.full_url, self.file.name)
    
    def __repr__(self):
        return str(self.file)
 
class Page(SiteResource):
    def __init__(self, a_file, node):    
        if not node:            
            raise ValueError("Page cannot exist without a node")
        super(Page, self).__init__(a_file, node) 
        self.process()

    def get_context_text(self):
        start = re.compile(r'.*?{%\s*hyde\s*(.*?)(%}|$)')
        end = re.compile(r'(.*?)(%})')
        fin = open(self.file.path,'r')
        started = False
        text = ''
        matcher = start
        for line in fin:
            match = matcher.match(line)
            if match:
                text = text + match.group(1)
                if started: 
                    break
                else:
                    matcher = end 
                    started = True
            elif started:
                text = text + line
        fin.close()
        return text

    def add_variables(self, page_vars):
        if not page_vars: return
        for key, value in page_vars.iteritems():
            if not hasattr(Page, key):
                setattr(Page, key, None)
            setattr(self, key, value)

    def process(self):
        text = self.get_context_text()
        import yaml
        context = yaml.load(text)
        if not context:
            context = {}
        self.add_variables(context) 

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
                
    def walk_resources(self):
        for node in self.walk():
            for resource in node.resources:
                yield resource

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
        self.site.child_added(node)
        return node
        
    def add_resource(self, a_file):
        resource = self._make_resource_from_file(a_file)
        self.resources.append(resource)
        self.site.resource_added(resource)
        return resource
        
    def remove_resource(self, resource):
        self.resources.remove(resource)
        self.site.resource_removed(resource)

    def _make_resource_from_file(self, a_file):
        return SiteResource(a_file, self)
        
    def find_node(self, folder):
        try:
            return self.site.nodemap[folder.path]
        except KeyError:
            return None
        
    find_child = find_node    
    
    def find_resource(self, a_file):
        try:
            return self.site.resourcemap[a_file.path]
        except KeyError:
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
        if self.url is None:
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
   
    def _make_resource_from_file(self, a_file):
        return Page(a_file, self)
    
    @property
    def target_folder(self):
        deploy_folder = self.site.target_folder
        return deploy_folder.child_folder_with_fragment(self.url)

    @property
    def temp_folder(self):
        temp_folder = self.site.temp_folder
        return temp_folder.child_folder_with_fragment(self.url)

    @property
    def fragment(self):
        return self.folder.get_fragment(self.site.content_folder)

    @property
    def url(self):
        return url.join(self.site.settings.SITE_ROOT,
                url.fixslash(        
                    self.folder.get_fragment(self.site.content_folder)))
    
    @property            
    def type(self):
      return "content"
          
class LayoutNode(SiteNode):
    
    @staticmethod
    def is_layout(site, folder):
        return (site.layout_folder.same_as(folder) or
                site.layout_folder.is_ancestor_of(folder))
                
    @property
    def fragment(self):
        return self.folder.get_fragment(self.site.layout_folder)
        
    @property
    def type(self):
        return "layout"          
          
class MediaNode(SiteNode):

    @staticmethod
    def is_media(site, folder):
        return (site.media_folder.same_as(folder) or
                site.media_folder.is_ancestor_of(folder))

    @property
    def fragment(self):
        return self.folder.get_fragment(self.site.media_folder)
    
    @property
    def url(self):
        return url.join(self.site.settings.SITE_ROOT,
                url.fixslash(        
                    self.folder.get_fragment(self.site.folder)))

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
    def __init__(self, settings, site_path):
        super(SiteInfo, self).__init__(Folder(site_path))
        self.settings = settings
        self.m = None
        self._stop = Event()
        self.nodemap = {site_path:self}
        self.resourcemap = {}

    @property
    def content_node(self):
        return self.nodemap[self.content_folder.path]
    
    @property
    def fragment(self):
        return ""
        
    @property
    def media_node(self):
        return self.nodemap[self.media_folder.path]    
    
    @property
    def layout_node(self):
        return self.nodemap[self.layout_folder.path]    
     
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
    
    def child_added(self, node):
        self.nodemap[node.folder.path] = node
        
    def resource_added(self, resource):
        self.resourcemap[resource.file.path] = resource
        
    def resource_removed(self, resource):
        del self.resourcemap[resource.file.path]
    
    def monitor(self, queue=None, waittime=10):
        if self.m and self.m.isAlive():
            raise "A monitor is currently running."
        self._stop.clear()    
        self.m = Thread(target=self.__monitor_thread__, 
                            kwargs={"waittime":waittime, "queue": queue})
        self.m.start()
        return self.m
    
    def dont_monitor(self):
        if not self.m or not self.m.isAlive():
            return
        self._stop.set()
        self.m.join()
        self._stop.clear()
        
    def __monitor_thread__(self, queue, waittime):
        while not self._stop.isSet():
            try:
                self.refresh(queue)
            except:
                if queue:
                    queue.put({"exception": True})
                raise
            if self._stop.isSet():
                break        
            time.sleep(waittime)
     
    def find_and_add_resource(self, a_file):
        resource = self.find_resource(a_file)        
        if resource:
            return resource
        node = self.find_and_add_node(a_file.parent)
        return node.add_resource(a_file)
        
    def find_and_add_node(self, folder):
        node = self.find_node(folder)
        if node:
            return node
        node = self.find_and_add_node(folder.parent)    
        return node.add_child(folder)
        
    def refresh(self, queue=None):
        site = self
        # Have to poll for changes since there is no reliable way
        # to get notification in a platform independent manner
        #                    
        class Visitor(object):
            def visit_file(self, a_file):
                resource = site.find_resource(a_file)
                change = None
                if not resource:
                   resource = site.find_and_add_resource(a_file)
                   change = "Added"
                elif resource.has_changes:
                   change = "Modified"
                if change:
                    if queue:
                       queue.put({
                           "change": change,
                           "resource": resource,
                           "exception": False
                       })
                    resource.last_known_modification_time = a_file.last_modified
     
        self.folder.walk(visitor=Visitor())
        for resource in self.walk_resources():
            if not resource.file.exists:
                if queue:
                    queue.put({
                        "change":"Deleted",
                        "resource":resource,
                        "exception": False
                    })
                resource.node.remove_resource(resource)
                