from hydeengine.file_system import File, Folder

class SiteNode(object):
    def __init__(self, folder, parent=None):
        self.folder = folder
        self.parent = parent
        
    @property
    def name(self):
        return self.folder.name
    
class SiteInfo(SiteNode):
    # def __init__(self, content_folder, layout_folder,  media_folder):
    #     self.content_folder = content_folder
    #     self.layout_folder = layout_folder
    #     self.media_folder - media_folder
    
    def __init__(self, site_path):
        self.site_path = site_path
        super(SiteInfo, self).__init__(self.site_path)
    
    
        