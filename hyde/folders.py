import sys, os
from file_system import *
from django.conf import settings

def load_processor(name):
    (module_name, dot, processor) = name.rpartition(".")
    __import__(module_name)
    module = sys.modules[module_name]
    return getattr(module, processor)


class HydeFolder(Folder):    
    def __init__(self, path, processors, ignore_root=False):
        super(HydeFolder, self).__init__(path)
        self.processors = processors
        self.default_processors = processors["*"]
        self.ignore_root = ignore_root
        
    def visit_folder(self, visitor, folder):
        self.current_processors = {}
        self.current_processors.update(self.default_processors)
        fragment = folder.get_fragment(self.path)
        if len(fragment) and self.processors.has_key(fragment):
            self.current_processors.update(self.processors[fragment])
        super(HydeFolder, self).visit_folder(visitor, folder)
    
    def visit_file(self, visitor, file):
        target = file.parent.create_mirror_folder(self, settings.TMP_DIR, self.ignore_root)
        file = file.copy_to(target)
        if file and file.exists and self.current_processors.has_key(file.extension):
            file_processors = self.current_processors[file.extension]
            for processor_name in file_processors:
                if file and file.exists:
                    processor = load_processor(processor_name)
                    file = processor.process(file)
        super(HydeFolder, self).visit_file(visitor, file)

class MediaFolder(HydeFolder):
    def __init__(self):
        super(MediaFolder, self).__init__(settings.MEDIA_DIR, settings.MEDIA_PROCESSORS)
            
class ContentFolder(HydeFolder):
    def __init__(self):
        super(ContentFolder, self).__init__(settings.CONTENT_DIR, settings.CONTENT_PROCESSORS)