import os, commands
from django.template.loader import render_to_string
from django.conf import settings
from file_system import File

class TemplateProcessor:
    @staticmethod
    def process(a_file):
        rendered = render_to_string(str(a_file), settings.CONTEXT)
        fout = open(str(a_file),'w')
        fout.write(rendered)
        fout.close()
        return a_file

## aym-cms code refactored into processors.

class CleverCSS:
    
    @staticmethod
    def process(a_file):
        import clevercss
        out_file = a_file.path_without_extension + ".css"
        fin = open(str(a_file), 'r')
        data = fin.read()
        fin.close()
        fout = open(out_file,'w')
        fout.write(clevercss.convert(data))
        fout.close()
        a_file.delete()
        return File(out_file)
        
class HSS:
    @staticmethod
    def process(a_file):
        out_file = a_file.path_without_extension + ".css"
        hss = settings.HSS_PATH
        if not hss or not os.path.exists(hss):
            raise ValueError("HSS Processor cannot be found at [%s]" % hss)
        status, output = commands.getstatusoutput(
        u"%s %s -output %s/" % (hss, str(a_file),
                                os.path.dirname(out_file)))
        if status > 0: 
            print output
            return None
        a_file.delete()
        return File(out_file)
        
class YUICompressor:
    @staticmethod
    def process(a_file):
        compress = settings.YUI_COMPRESSOR
        if not compress or not os.path.exists(compress):
            raise ValueError(
            "YUI Compressor cannot be found at [%s]" % compress)
            
        tmp_file = str(a_file) + ".z-tmp"
        status, output = commands.getstatusoutput(
        u"java -jar %s %s > %s" % (compress, str(a_file), tmp_file))
        if status > 0: 
            print output
        else:           
            commands.getoutput(u"mv %s %s" % (tmp_file, str(a_file)))
        return a_file