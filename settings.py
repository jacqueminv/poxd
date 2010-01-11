import os
import logging

DEBUG=True
LOG_LEVEL = logging.INFO
DATE_FORMAT = "j F Y"
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

MD_EXTENSIONS = ['footnotes']
PYGMENTS_OPTIONS = {'cssclass':'syntax'}
DEFAULT_CATEGORY = 'divers'

#Directories
LAYOUT_DIR = os.path.join(ROOT_PATH, 'layout')
CONTENT_DIR = os.path.join(ROOT_PATH, 'content')
MEDIA_DIR = os.path.join(ROOT_PATH, 'media')
DEPLOY_DIR = os.path.join(ROOT_PATH, 'deploy')
TMP_DIR = os.path.join(ROOT_PATH, 'deploy_tmp')

SITEMAP_FILE = os.path.join(TMP_DIR, 'sitemap.xml')
SITEMAP_GENERATOR = os.path.join(ROOT_PATH,  "../lib/sitemap_gen-1.4/sitemap_gen.py")


BACKUPS_DIR = os.path.join(ROOT_PATH, 'backups')
BACKUP = False

SITE_ROOT = "/"
SITE_WWW_URL = "http://www.poxd.org/" #"http://localhost:8080/"
SITE_NAME = "PoXd"
SITE_AUTHOR = "Valentin Jacquemin"
SITE_AUTHOR_EMAIL = "jacqueminv@gmail.com"
LANGUAGE_CODE = 'fr'

#Url Configuration
GENERATE_ABSOLUTE_FS_URLS = True

# Clean urls causes Hyde to generate urls without extensions. Examples:
# http://example.com/section/page.html becomes
# http://example.com/section/page/, and the listing for that section becomes
# http://example.com/section/
# The built-in CherryPy webserver is capable of serving pages with clean urls
# without any additional configuration, but Apache will need to use Mod_Rewrite
# to map the clean urls to the actual html files.  The HtaccessGenerator site
# post processor is capable of automatically generating the necessary
# RewriteRules for use with Apache.
GENERATE_CLEAN_URLS = False

# A list of filenames (without extensions) that will be considered listing
# pages for their enclosing folders.
# LISTING_PAGE_NAMES = ['index']
LISTING_PAGE_NAMES = ['listing', 'index', 'default']

# Determines whether or not to append a trailing slash to generated urls when
# clean urls are enabled.
APPEND_SLASH = False

# {folder : extension : (processors)}
# The processors are run in the given order and are chained.
# Only a lone * is supported as an indicator for folders. Path 
# should be specified. No wildcard card support yet.
 
# Starting under the media folder. For example, if you have media/css under 
# your site root,you should specify just css. If you have media/css/ie you 
# should specify css/ie for the folder name. css/* is not supported (yet).

# Extensions do not support wildcards.

MEDIA_PROCESSORS = {
    '*':{
        '.css':('hydeengine.media_processors.TemplateProcessor',
                'hydeengine.media_processors.YUICompressor',),
         '.js':(
                'hydeengine.media_processors.TemplateProcessor',
                'hydeengine.media_processors.YUICompressor',)
    } 
}

CONTENT_PROCESSORS = {}
SITE_PRE_PROCESSORS = {
    'blog': {
        'hydeengine.site_pre_processors.CategoriesManager': {'node':'blog'},
        },
    '/': {
        'hydeengine.site_pre_processors.NodeInjector' : {
               'variable' : 'blog_node',
               'path' : 'content/blog'
        }
    }
}
SITE_POST_PROCESSORS = {
     'media/js': {
            'hydeengine.site_post_processors.FolderFlattener' : {
                    'remove_processed_folders': True,
                    'pattern':"*.js"
            }
        },
    '/' : {
        'hydeengine.site_post_processors.GoogleSitemapGenerator' : {
            'sitemap_file':SITEMAP_FILE,
            'generator': SITEMAP_GENERATOR,
            }
        },
    'blog': {
            'hydeengine.site_post_processors.RssGenerator': {
                'generate_by_categories': True
                }
            }
}

GIT_HUB = "http://github.com/poxd"
CONTEXT = {
    'GENERATE_CLEAN_URLS': GENERATE_CLEAN_URLS,
    'links': {
        "jekyll": "http://github.com/mojombo/jekyll/tree/master",
        "hyde": "http://ringce.com/hyde"
        }
}

FILTER = { 
    'include': (".htaccess",),
    'exclude': (".*","*~")
}        


#Processor Configuration

# path for YUICompressor, or None if you don't
# want to compress JS/CSS. Project homepage:
# http://developer.yahoo.com/yui/compressor/
YUI_COMPRESSOR = "./lib/yuicompressor-2.4.1.jar"
#YUI_COMPRESSOR = None 

# path for HSS, which is a preprocessor for CSS-like files (*.hss)
# project page at http://ncannasse.fr/projects/hss
#HSS_PATH = "./lib/hss-1.0-osx"
HSS_PATH = None # if you don't want to use HSS

#Django settings

TEMPLATE_DIRS = (LAYOUT_DIR, CONTENT_DIR, TMP_DIR, MEDIA_DIR)

INSTALLED_APPS = (
    'typogrify',
    'hydeengine',
    'django.contrib.webdesign',
)
