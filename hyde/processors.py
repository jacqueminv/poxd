import os, shutil, commands
from django.template.loader import render_to_string
from django.conf import settings
from hyde import PathUtil

class CopyProcessor:
	
	@staticmethod
	def process(file):
		tmp_media_dir = PathUtil.mirror_dir_tree(os.path.dirname(file), settings.MEDIA_DIR, settings.TMP_DIR)
		if not os.path.exists(tmp_media_dir):
			os.makedirs(tmp_media_dir)
		shutil.copy(file, tmp_media_dir)
		return os.path.join(tmp_media_dir, os.path.basename(file))

class CleverCSS:
	
	@staticmethod
	def process(file):
		import clevercss
		(file_name, extension) = os.path.splitext(file)
		out_file = file_name + ".css"
		fin = open(file, 'r')
		data = fin.read()
		fin.close()
		fout = open(out_file,'w')
		fout.write(clevercss.convert(data))
		fout.close()
		os.remove(file)
		return out_file
		
class HSS:
	@staticmethod
	def process(file):
		(file_name, extension) = os.path.splitext(file)
		out_file = file_name + ".css"
		hss = settings.HSS_PATH
		if not hss or not os.path.exists(hss):
			raise ValueError("HSS Processor cannot be found at [%s]" % hss)
		s, o = commands.getstatusoutput(u"%s %s -output %s/" % (hss, file, os.path.dirname(out_file)))
		if s > 0: 
			print o
			return None
		os.remove(file)
		return out_file
		
class YUICompressor:
	@staticmethod
	def process(file):
		compress = settings.YUI_COMPRESSOR
		if not compress or not os.path.exists(compress):
			raise ValueError("YUI Compressor cannot be found at [%s]" % compress)
		tmp_file = file + ".z-tmp-"
		s,o = commands.getstatusoutput(u"java -jar %s %s > %s" % (compress, file, tmp_file))
		if s > 0: 
			print o
		else:			
			commands.getoutput(u"mv %s %s" % (tmp_file, file))
		return file