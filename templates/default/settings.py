import os

ROOT_PATH = os.path.dirname(__file__)

#Directories
LAYOUT_DIR = os.path.join(ROOT_PATH, 'layout')
CONTENT_DIR = os.path.join(ROOT_PATH, 'content')
MEDIA_DIR = os.path.join(ROOT_PATH, 'media')
DEPLOY_DIR = os.path.join(ROOT_PATH, 'deploy')
TMP_DIR = os.path.join(ROOT_PATH, 'deploy_tmp')
BACKUPS_DIR = os.path.join(ROOT_PATH, 'backups')

SITE_NAME = "Hyde"
DATETIME_FORMAT = "%Y-%m-%d %H:%i"

# {folder : extension : (processors)}
# The processors are run in the given order and are chained.
# Only a lone * is supported as an indicator for folders. Path 
# shoud be specifed. No wildcard card support yet.
 
# Starting under the media folder. For example, if you have media/css under 
# your site root,you should specify just css. If you have media/css/ie you 
# should specify css/ie for the folder name. css/* is not supported (yet).

# Extensions do not support wildcards.
GENERATE_ABSOLUTE_FS_URLS = True

MEDIA_PROCESSORS = {
    '*':{
        '.css':('hydeengine.media_processors.YUICompressor',),
        '.ccss':('hydeengine.media_processors.CleverCSS', 'hydeengine.media_processors.YUICompressor',),
        '.hss':('hydeengine.media_processors.HSS', 'hydeengine.media_processors.YUICompressor',),
        '.js':('hydeengine.media_processors.YUICompressor',)
    } 
}

CONTENT_PROCESSORS = {
    '*': {
        '.html':('hydeengine.content_processors.YAMLContentProcessor',
                # If you want to create a dictionary in python instead:
                # 'hydeengine.content_processors.PyContentProcessor'
                # Needs py.code.
        )
    }
}

CONTEXT = {

}

#Processor Configuration

# path for YUICompressor, or None if you don't
# want to compress JS/CSS. Project homepage:
# http://developer.yahoo.com/yui/compressor/
YUI_COMPRESSOR = "./tools/yuicompressor-2.4.1.jar"
#YUI_COMPRESSOR = None 

# path for HSS, which is a preprocessor for CSS-like files (*.hss)
# project page at http://ncannasse.fr/projects/hss
HSS_PATH = "./tools/hss-1.0-osx"
#HSS_PATH = None # if you don't want to use HSS




#Django settings

TEMPLATE_DIRS = ( LAYOUT_DIR, CONTENT_DIR, TMP_DIR)

INSTALLED_APPS = (
    'hydeengine',
    'django.contrib.webdesign',
)

