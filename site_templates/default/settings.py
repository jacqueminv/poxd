import os

ROOT_PATH = os.path.dirname(__file__)

#Directories
SITE_TEMPLATE_DIR = os.path.join(ROOT_PATH, 'templates')
CONTENT_DIR = os.path.join(ROOT_PATH, 'content')
MEDIA_DIR = os.path.join(ROOT_PATH, 'media')
DEPLOY_DIR = os.path.join(ROOT_PATH, 'deploy')
TMP_DIR = os.path.join(ROOT_PATH, 'deploy_tmp')
BACKUPS_DIR = os.path.join(ROOT_PATH, 'backups')


# {folder : extension : (processors)}
# The processors are run in the given order and are chained.
# Only a lone * is supported for folders. Path shoud be specifed 
# starting under the media folder. For example, if you have media/css under 
# your site root,you should specify just css. If you have media/css/ie you 
# should specify css/ie for the folder name. css/* is not supported (yet).

# Extensions do not support wildcards.
GENERATE_ABSOLUTE_FS_URLS = False

MEDIA_PROCESSORS = {
	'*':{
		'.css':('hyde.processors.YUICompressor',),
		'.ccss':('hyde.processors.CleverCSS', 'hyde.processors.YUICompressor',),
		'.hss':('hyde.processors.HSS', 'hyde.processors.YUICompressor',),
		'.js':('hyde.processors.YUICompressor',)
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

TEMPLATE_DIRS = ( SITE_TEMPLATE_DIR, CONTENT_DIR, )

INSTALLED_APPS = (
    'hyde',
    'django.contrib.webdesign'
)


