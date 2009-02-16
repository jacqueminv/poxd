import os, commands
from django.template.loader import render_to_string
from django.conf import settings
from file_system import File

class TemplateProcessor:
    @staticmethod
    def process(resource):
        rendered = render_to_string(resource.file.path, settings.CONTEXT)
        fout = open(resource.file.path,'w')
        fout.write(rendered)
        fout.close()

## aym-cms code refactored into processors.
class CleverCSS:    
    @staticmethod
    def process(resource):
        import clevercss
        data = resource.file.read_all()
        out = clevercss.convert(data)
        resource.file.write(out)

class HSS:
    @staticmethod
    def process(resource):
        out_file = File(resource.file.path_without_extension + ".css")
        hss = settings.HSS_PATH
        if not hss or not os.path.exists(hss):
            raise ValueError("HSS Processor cannot be found at [%s]" % hss)
        status, output = commands.getstatusoutput(
        u"%s %s -output %s/" % (hss, resource.file.path, out_file.parent.path))
        if status > 0: 
            print output
            return None
        resource.file.delete()
        out_file.copy_to(resource.file.path)
        out_file.delete()
        
class YUICompressor:
    @staticmethod
    def process(resource):
        compress = settings.YUI_COMPRESSOR
        if not compress or not os.path.exists(compress):
            raise ValueError(
            "YUI Compressor cannot be found at [%s]" % compress)
            
        tmp_file = File(resource.file.path + ".z-tmp")
        status, output = commands.getstatusoutput(
        u"java -jar %s %s > %s" % (compress, resource.file.path, tmp_file.path))
        if status > 0: 
            print output
        else:
            resource.file.delete()
            tmp_file.move_to(resource.file.path)