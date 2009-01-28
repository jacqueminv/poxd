import imp, sys, os, shutil
from django.conf import settings
from django.core.management import setup_environ
from path_util import PathUtil
from django.template.loader import render_to_string
from django.template import add_to_builtins
from file_system import File, Folder
from folders import MediaFolder, ContentFolder, TempFolder
from renderer import build_sitemap, render_pages

class Generator(object):
    def __init__(self, site_path):
        super(Generator, self).__init__()
        self.site_path = os.path.abspath(os.path.expandvars(
                                        os.path.expanduser(site_path)))
    
    def generate(self, deploy_path):
        try:
            imp.load_source("hyde_site_settings",
                            os.path.join(self.site_path,"settings.py"))
        except Exception, err:
            print "Cannot Import Site Settings"
            print err
            raise ValueError(
            "The given site_path [%s] does not contain a hyde site. \
            Give a valid path or run -init to create a new site."  
            %  self.site_path
            )
            
        try:
            os.environ['DJANGO_SETTINGS_MODULE'] = u"hyde_site_settings"
        except Exception, err:
            print "Site settings are not defined properly"
            print err
            raise ValueError(
            "The given site_path [%s] has invalid settings. \
            Give a valid path or run -init to create a new site."  
            %  self.site_path
            )
        
        tmp_folder = Folder(settings.TMP_DIR)
        deploy_folder = Folder(
                            (deploy_path, settings.DEPLOY_DIR)
                            [not deploy_path])
                            
        if deploy_folder.exists and settings.BACKUP:
            backup_folder = Folder(settings.BACKUPS_DIR).make()
            deploy_folder.backup(backup_folder)

        tmp_folder.delete()
        tmp_folder.make()
        
        add_to_builtins('hydeengine.templatetags.hydetags')
        add_to_builtins('hydeengine.templatetags.aym')
        build_sitemap()
        
        MediaFolder().walk() 
        render_pages()
        
        TempFolder().walk()
        
        deploy_folder.delete()
        deploy_folder.make()
        deploy_folder.move_contents_of(tmp_folder)
        tmp_folder.delete()
    
class Initializer(object):
    def __init__(self, site_path):
        super(Initializer, self).__init__()
        self.site_path = Folder(site_path)

    def initialize(self, root, template, force):
        if not template:
            template = "default"
        root_folder = Folder(root)
            
        template_dir = root_folder.child_folder("templates", template)
        
        if not template_dir.exists:
            raise ValueError(
            "Cannot find the specified template[%s]." % template_dir)
            
        if self.site_path.exists:    
            files = os.listdir(self.site_path.path)
            PathUtil.filter_hidden_inplace(files)
            if len(files) and not force:
                raise ValueError(
                "The site_path[%s] is not empty." % self.site_path)
            else:
                self.site_path.delete()
        self.site_path.make()
        self.site_path.copy_contents_of(template_dir)