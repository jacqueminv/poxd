import os, shutil, commands
from django.template.loader import render_to_string
from django.conf import settings
from hyde import PathUtil
from file_system import *

class TemplateProcessor:
    @staticmethod
    def process(file):
        rendered = render_to_string(str(file), settings.CONTEXT)
        fout = open(str(file),'w')
        fout.write(rendered)
        fout.close()
        return file

class CleverCSS:
    
    @staticmethod
    def process(file):
        import clevercss
        out_file = file.name_without_extension + ".css"
        fin = open(str(file), 'r')
        data = fin.read()
        fin.close()
        fout = open(out_file,'w')
        fout.write(clevercss.convert(data))
        fout.close()
        os.remove(str(file))
        return File(out_file)
        
class HSS:
    @staticmethod
    def process(file):
        out_file = file.name_without_extension + ".css"
        hss = settings.HSS_PATH
        if not hss or not os.path.exists(hss):
            raise ValueError("HSS Processor cannot be found at [%s]" % hss)
        s, o = commands.getstatusoutput(u"%s %s -output %s/" % (hss, str(file), os.path.dirname(out_file)))
        if s > 0: 
            print o
            return None
        os.remove(str(file))
        return File(out_file)
        
class YUICompressor:
    @staticmethod
    def process(file):
        compress = settings.YUI_COMPRESSOR
        if not compress or not os.path.exists(compress):
            raise ValueError("YUI Compressor cannot be found at [%s]" % compress)
        tmp_file = str(file) + ".z-tmp"
        s,o = commands.getstatusoutput(u"java -jar %s %s > %s" % (compress, str(file), tmp_file))
        if s > 0: 
            print o
        else:           
            commands.getoutput(u"mv %s %s" % (tmp_file, str(file)))
        return file