import os
import shutil
import codecs
import fnmatch
from datetime import datetime
from distutils import dir_util, file_util
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

    def delete(self):
        if self.exists:
            os.remove(self.path)
            
    def changed_since(self, basetime):
        updated = os.path.getmtime(self.path)
        return  datetime.fromtimestamp(updated) > basetime
        
    def older_than(self, another_file):
        return (os.path.getmtime(another_file.path) > 
                                os.path.getmtime(self.path))

    @property
    def path_without_extension(self):
        return os.path.splitext(self.path)[0]
        
    @property
    def name_without_extension(self):
        return os.path.splitext(self.name)[0]
        
    @property
    def extension(self):
        return os.path.splitext(self.path)[1]
        
    @property
    def kind(self):
        return self.extension.lstrip(".")
        
    def move_to(self, destination):
        shutil.move(self.path, str(destination))
        return self._get_destination(destination)

    def copy_to(self, destination):
        shutil.copy(self.path, str(destination))
        return self._get_destination(destination)
        
    def write(self, text):
        fout = codecs.open(self.path,'w')
        fout.write(text)
        fout.close()
        
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
        
        
    def same_as(self, other_folder):
        return os.path.samefile(self.path, other_folder.path)
    
    def is_parent_of(self, other_entity):
        return self.same_as(other_entity.parent)

    def child(self, name):
        return os.path.join(self.path, name)
        
    def child_folder(self, *args):
        return Folder(os.path.join(self.path, *args))
    
    def child_folder_with_fragment(self, fragment):
        return Folder(os.path.join(self.path, fragment))
        
    def get_fragment(self, root):
        return PathUtil.get_path_fragment(str(root), self.path)
        
    def get_mirror_folder(self, root, mirror_root, ignore_root=False):
        path = PathUtil.get_mirror_dir(
                self.path, str(root), str(mirror_root), ignore_root)
        return Folder(path)
        
    def create_mirror_folder(self, root, mirror_root, ignore_root=False):
        mirror_folder = self.get_mirror_folder(
                        root, mirror_root, ignore_root)
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
        
    def move_folder_from(self, source, incremental=False):
        self.copy_folder_from(source, incremental)
        shutil.rmtree(str(source))

    def copy_folder_from(self, source, incremental=False):
        dir_util.copy_tree(str(source), 
                        self.child(source.name), 
                        update=incremental)
                        
    def move_contents_of(self, source, move_empty_folders=True, 
                        incremental=False):
        class Mover:
            @staticmethod
            def visit_folder(folder):
                self.move_folder_from(folder, incremental)
            @staticmethod                
            def visit_file(a_file):
                self.move_file_from(a_file, incremental)
        source.list(Mover, move_empty_folders)
         
    def copy_contents_of(self, source, copy_empty_folders=True,
                        incremental=False):
        class Copier:
            @staticmethod
            def visit_folder(folder):
                self.copy_folder_from(folder, incremental)
            @staticmethod                
            def visit_file(a_file):
                self.copy_file_from(a_file, incremental)
        source.list(Copier, copy_empty_folders)    
        
    def move_file_from(self, source, incremental=False):
        self.copy_file_from(source, incremental)
        source.delete()

    def copy_file_from(self, source, incremental=False):
        file_util.copy_file(str(source), self.path, update=incremental)

    def list(self, visitor, list_empty_folders=True):
        a_files = os.listdir(self.path)
        for a_file in a_files:
            path = os.path.join(self.path, str(a_file))
            if os.path.isdir(path):
                if not list_empty_folders:
                    if Folder(path).isEmpty():
                        continue
                visitor.visit_folder(Folder(path))
            else:
                visitor.visit_file(File(path))
    
    def isEmpty(self):
        paths = os.listdir(self.path)
        for path in paths:
            if os.path.isdir(path):
                if not Folder(path).isEmpty():
                    return False
            else:
                return False    
        return True
                
    def walk(self, visitor = None, pattern = None):
        for root, dirs, a_files in os.walk(self.path):
            PathUtil.filter_hidden_inplace(dirs)
            PathUtil.filter_hidden_inplace(a_files)
            folder = Folder(root)
            self.visit_folder(visitor, folder)
            for a_file in a_files:
                if not pattern or fnmatch.fnmatch(a_file, pattern):
                    self.visit_file(visitor, File(folder.child(a_file)))
        self.visit_complete(visitor)
                
    def visit_folder(self, visitor, folder):
        if visitor and hasattr(visitor,'visit_folder'):
            visitor.visit_folder(folder)

    def visit_file(self, visitor, a_file):
        if visitor and hasattr(visitor,'visit_file'):
            visitor.visit_file(a_file)
            
    def visit_complete(self, visitor):
        if visitor and hasattr(visitor,'visit_complete'):
            visitor.visit_complete()