import os, shutil
from path_util import PathUtil

class FileSystemEntity(object):
    def __init__(self, path):
        super(FileSystemEntity, self).__init__()
        if path is FileSystemEntity:
            self.path = path.path
        else:
            self.path = path
    
    def __str__(self):
        return self.path
        
    def __repr__(self):
        return self.path

    @property    
    def exists(self):
        return os.path.exists(self.path)

    @property    
    def isdir(self):
        return os.path.isdir(self.path)
    
    @property 
    def stats(self):
        return os.stat(self.path)
        
    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def parent(self):
        return Folder(os.path.dirname(self.path))    
        
    def _get_destination(self, destination):
        if os.path.isdir(str(destination)):
            target = destination.child(self.name)
            if os.path.isdir(self.path):
                return Folder(target)
            else: return File(target)
        else:
            return destination
            
class File(FileSystemEntity):
    def __init__(self, path):
        super(File, self).__init__(path)
    
    def has_extension(self, extension):
        return self.extension  == extension
        
    @property
    def name_without_extension(self):
        return os.path.splitext(self.path)[0]
        
    @property
    def extension(self):
        return os.path.splitext(self.path)[1]
        
    def move_to(self, destination):
        shutil.move(self.path, str(destination))
        return self._get_destination(destination)

    def copy_to(self, destination):
        shutil.copy(self.path, str(destination))
        return self._get_destination(destination)
        
class Folder(FileSystemEntity):
    
    def __init__(self, path):
        super(Folder, self).__init__(path)

    def __str__(self):
        return self.path
        
    def __repr__(self):
        return self.path  

    def delete(self):
        if self.exists:
            shutil.rmtree(self.path)
    
    def make(self):
        try:
            if not self.exists:
                os.makedirs(self.path)
        except:
            pass
        return self
        
    def child(self, name):
        return os.path.join(self.path, name)
        
    def get_fragment(self, root):
        return PathUtil.get_path_fragment(str(root), self.path)
        
    def get_mirror_folder(self, root, mirror_root, ignore_root=False):
        path = PathUtil.get_mirror_dir(self.path, str(root), str(mirror_root), ignore_root)
        return Folder(path)
        
    def create_mirror_folder(self, root, mirror_root, ignore_root=False):
        mirror_folder = self.get_mirror_folder(root, mirror_root, ignore_root)
        mirror_folder.make()
        return mirror_folder
    
    def backup(self, destination):
        new_name = self.name
        count = 0
        dest = Folder(destination.child(new_name))
        while(True):
            dest = Folder(destination.child(new_name))
            if not dest.exists:
                break
            else:
                count = count + 1
                new_name = self.name + str(count)
        print self
        print destination
        print dest        
        dest.make()
        dest.move_contents_of(self)
        self.delete()
        return dest
         
    def move_to(self, destination):
        shutil.copytree(self.path, str(destination))
        shutil.rmtree(str(destination))
        return self._get_destination(destination)
        
    def copy_to(self, destination):
        shutil.copytree(self.path, str(destination))
        return self._get_destination(destination)
        
    def move_folder_from(self, source):
        self.copy_folder_from(source)
        shutil.rmtree(str(source))

    def copy_folder_from(self, source):
        shutil.copytree(str(source), self.child(source.name))
        
    def move_contents_of(self, source):
        class Mover:
            @staticmethod
            def visit_folder(folder):
                self.move_folder_from(folder)
            @staticmethod                
            def visit_file(file):
                self.move_file_from(file)
        source.list(Mover)
         
    def copy_contents_of(self, source):
        class Copier:
            @staticmethod
            def visit_folder(folder):
                self.copy_folder_from(folder)
            @staticmethod                
            def visit_file(file):
                self.copy_file_from(file)
        source.list(Copier)    
        
    def move_file_from(self, source):
        shutil.move(str(source), self.path)

    def copy_file_from(self, source):
        shutil.copy(str(source), self.path) 

    def list(self, visitor):
        files = os.listdir(self.path)
        for file in files:
            path = os.path.join(self.path, str(file))
            if os.path.isdir(path):
                visitor.visit_folder(Folder(path))
            else:
                visitor.visit_file(File(path))
                
    def walk(self, visitor = None):
        for root, dirs, files in os.walk(self.path):
            PathUtil.filter_hidden_inplace(dirs)
            PathUtil.filter_hidden_inplace(files)
            self.visit_folder(visitor, Folder(root))
            for file in files:
                self.visit_file(visitor, File(os.path.join(root,str(file))))
                
    def visit_folder(self, visitor, folder):
        if visitor:
            vistor.visit_folder(folder)
        
    def visit_file(self, visitor, file):
        if visitor:
            vistor.visit_file(self, file)