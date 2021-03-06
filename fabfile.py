#/usr/bin/env python

from fabric.api import *
import os, os.path
import fabric.contrib.project as project
#from smooshy import smoosher

PROD = 'poxd.webfactional.com'
DEST_PATH = '/home/poxd/webapps/poxdhyde/'
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DEPLOY_PATH = os.path.join(ROOT_PATH, 'deploy')

def clean():
    local('rm -rf ./deploy')

def regen():
    clean()
    local('hyde -g -s .')

def serve():
    local('hyde -w -s . -k')

def reserve():
    regen()
    serve()

def smush():
    pass
#    smoosher.recursive_smoosher(["./media/images/"])

@hosts(PROD)
def publish():
    regen()
    project.rsync_project(
        remote_dir=DEST_PATH,
        local_dir=DEPLOY_PATH.rstrip('/') + '/'
    )
    run("chmod 644 webapps/poxdhyde/media/images/*")
