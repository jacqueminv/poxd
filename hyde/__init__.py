import imp, sys, os, shutil
from django.conf import settings
from django.core.management import setup_environ
from path_util import PathUtil
from django.template.loader import render_to_string
from django.template import add_to_builtins
from file_system import *
from folders import *
from renderer import *

class Generator(object):
    def __init__(self, site_path):
        super(Generator, self).__init__()
        self.site_path = os.path.abspath(os.path.expandvars(os.path.expanduser(site_path)))
    
    def generate(self, deploy_path):
        try:
            imp.load_source("hyde_site_settings", os.path.join(self.site_path,"settings.py"))
        except Exception, e:
            print "Cannot Import Site Settings"
            raise ValueError("The given site_path [%s] does not contain a hyde site. Give a valid path or run -init to create a new site." % self.site_path)
            
        try:
            os.environ['DJANGO_SETTINGS_MODULE'] = u"hyde_site_settings"
        except Exception, e:
            print "Site settings are not defined properly"
            raise ValueError("The given site_path [%s] does not contain a hyde site. Give a valid path or run -init to create a new site." % self.site_path)
        
        tmp_folder = Folder(settings.TMP_DIR)
        backup_folder = Folder(settings.BACKUPS_DIR).make()
        deploy_folder = Folder((deploy_path, settings.DEPLOY_DIR)[not deploy_path])
        media_folder = Folder(settings.MEDIA_DIR)
        
        if(deploy_folder.exists):
            deploy_folder.backup(backup_folder)

        tmp_folder.delete()
        tmp_folder.make()

        if settings.GENERATE_ABSOLUTE_FS_URLS:
            media_root = deploy_folder.child(media_folder.name)
        else:
            media_root = os.sep + media_folder.name
            
        settings.CONTEXT['media'] = media_root
        MediaFolder().walk() 
           
        add_to_builtins('hyde.templatetags.hydetags')
        add_to_builtins('hyde.templatetags.aym')
        
        post_process_site(render_pages())
        
        deploy_folder.make()
        deploy_folder.move_contents_of(tmp_folder)
        tmp_folder.delete()
    
    
    
class Initializer(object):
    def __init__(self, site_path):
        super(Initializer, self).__init__()
        self.site_path = os.path.abspath(os.path.expandvars(os.path.expanduser(site_path)))

    def initialize(self, root, template):
        if not template:
            template = "default"
        template_dir = os.path.join(root, "site_templates", template)
        if not os.path.exists(template_dir):
            raise ValueError("Cannot find the specified template[%s]." % template_dir)
            
        if not os.path.exists(self.site_path):
            os.makedirs(self.site_path)
        else:
            files = os.listdir(self.site_path)
            PathUtil.filter_hidden_inplace(files)
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