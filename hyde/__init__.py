import imp, sys, os, shutil
from django.conf import settings
from django.core.management import setup_environ
from hyde.path_util import PathUtil
from processors import CopyProcessor
from django.template.loader import render_to_string
from django.template import add_to_builtins
from context_processor import ContextProcessor

class MediaProcessor:

	@staticmethod
	def process_media_dir(media_dir):
		default_processors = settings.MEDIA_PROCESSORS['*']
		for root, dirs, files in os.walk(media_dir):
			processors = {}
			processors.update(default_processors)
			fragment = PathUtil.get_path_fragment(media_dir, root)
			if len(fragment) and settings.MEDIA_PROCESSORS.has_key(fragment):
				processors.update(settings.MEDIA_PROCESSORS[fragment])
				
			for file in files:
				(file_name, extension) = os.path.splitext(file)
				full_path = os.path.join(root, file)
				full_path = CopyProcessor.process(full_path)
				if processors.has_key(extension):
					file_processors = processors[extension]
					for processor_name in file_processors:
						processor = MediaProcessor.load_processor(processor_name)
						full_path = processor.process(full_path)
					
	
	@staticmethod
	def load_processor(name):
		(module_name, dot, processor) = name.rpartition(".")
		__import__(module_name)
		module = sys.modules[module_name]
		return getattr(module, processor)
		
class Generator(object):
	def __init__(self, site_path):
		super(Generator, self).__init__()
		self.site_path = os.path.abspath(os.path.expandvars(os.path.expanduser(site_path)))
	
	def generate(self, deploy_path):
		try:
			imp.load_source("hyde_site_settings", os.path.join(self.site_path,"settings.py"))
			os.environ['DJANGO_SETTINGS_MODULE'] = u"hyde_site_settings"
		except Exception, e:
			print e
			raise ValueError("The given site_path [%s] does not contain a hyde site. Give a valid path or run -init to create a new site." % self.site_path)
			
		if not deploy_path:
			deploy_path = settings.DEPLOY_DIR
			
		if os.path.exists(deploy_path):
			statinfo = os.stat(deploy_path)
			if not os.path.exists(settings.BACKUPS_DIR):
				os.makedirs(settings.BACKUPS_DIR)
			dest = os.path.join(settings.BACKUPS_DIR, statinfo.st_ctime)
			shutil.copytree(deploy_path, dest)
			shutil.rmtree(deploy_path)
			
		if os.path.exists(settings.TMP_DIR):
			shutil.rmtree(settings.TMP_DIR)
			
		MediaProcessor.process_media_dir(settings.MEDIA_DIR)
		self.render_pages()
	
	def render_pages(self):
		add_to_builtins('hyde.templatetags.hydetags')
		context = settings.CONTEXT
		out_dir = settings.TMP_DIR
		for root, dirs, files in os.walk(settings.CONTENT_DIR):
			PathUtil.filter_hidden_inplace(dirs)
			PathUtil.filter_hidden_inplace(files)
			for page in files:
				page_path = os.path.join(root, page)
				page_context = ContextProcessor.get_page_context(context, page_path)
				rendered = render_to_string(os.path.join(root,page), page_context)
				source_dir = root
				page_out_dir = PathUtil.mirror_dir_tree(source_dir, settings.CONTENT_DIR, out_dir, ignore_root=True)
				page_path = os.path.join(page_out_dir,page)
				fout = open(page_path,'w')
				fout.write(rendered)
				fout.close()
	
class Initializer(object):
	def __init__(self, site_path):
		super(Initializer, self).__init__()
		self.site_path = os.path.abspath(os.path.expandvars(os.path.expanduser(site_path)))

	def initialize(self, root, template):
		if not template:
			template = "default"
		template_dir = os.path.join(root, "site_templates", template)
		if not os.path.exists(template_dir):
			raise ValueError("Cannot find the specified template[%s]." % template)
			
		if not os.path.exists(self.site_path):
			os.makedirs(self.site_path)
		else:
			files = os.listdir(self.site_path)
			if len(files):
				raise ValueError("The site_path[%s] is not empty." % self.site_path)
			
		files = os.listdir(template_dir)
		for file in files:
			source = os.path.join(template_dir, file)
			dest = os.path.join(self.site_path, file)
			if os.path.isdir(source):
				shutil.copytree(source, dest)
			else:
				shutil.copy(source, dest)
		# hyde_dest = os.path.join(self.site_path, "hyde")
		# os.mkdir(hyde_dest)		
		# hyde_source = os.path.join(root, "hyde", "templatetags")
		# shutil.copy(os.path.join(hyde_source, "__init__.py"), hyde_dest)
		# hyde_dest = os.path.join(hyde_dest, "templatetags")
		# shutil.copytree(hyde_source, hyde_dest)

