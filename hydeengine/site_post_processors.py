from django.conf import settings
from file_system import File

class FolderFlattener:
    
    @staticmethod
    def process(folder, params):
        class Flattener:
            def __init__(self, folder, params):
                self.folder = folder
                self.remove_processed_folders = \
                 params["remove_processed_folders"]
                self.previous_folder = None
            
            def visit_file(self, file):
                if not self.folder.is_parent_of(file):
                    file.copy_to(self.folder)
                
            def visit_folder(self, this_folder):                
                if self.previous_folder and self.remove_processed_folders:
                    self.previous_folder.delete()
                if not self.folder.same_as(this_folder):
                    self.previous_folder = this_folder
                    
            def visit_complete(self):
                if self.previous_folder and self.remove_processed_folders:
                    self.previous_folder.delete()

        folder.walk(Flattener(folder, params), params["pattern"])
        

        