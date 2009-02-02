#!/usr/bin/env python2
import os, sys
from optparse import OptionParser
from hydeengine import Generator, Initializer, Server

#import cProfile

PROG_ROOT = os.path.dirname(os.path.abspath( __file__ ))

def main(argv):
    parser = OptionParser()
    parser.add_option("-s", "--sitepath", 
                        dest = "site_path")
    parser.add_option("-i", "--init", action = 'store_true', 
                        dest = "init", default = False)
    parser.add_option("-f", "--force", action = 'store_true', 
                        dest = "force_init", default=False)
    parser.add_option("-t", "--template", 
                        dest = "template")
    parser.add_option("-g", "--generate", action = "store_true",
                        dest = "generate", default = False)
    parser.add_option("-d", "--deploy_to", 
                        dest = "deploy_to")
    parser.add_option("-w", "--webserve", action = "store_true",
                        dest = "webserve", default = False)

    (options, args) = parser.parse_args()
    
    if len(args):
        parser.error("Unexpected arguments encountered.")
        
    if not options.site_path:
        options.site_path = os.getcwdu()
    
    if options.init:
        initializer = Initializer(options.site_path)
        try:
            initializer.initialize(PROG_ROOT,
                        options.template, options.force_init)
        except ValueError, err:
            parser.error(err)
    if options.generate:
        generator = Generator(options.site_path)
        try:
            generator.generate(options.deploy_to)
        except ValueError, err:
            parser.error(err)
    if options.webserve:
        server = Server(options.site_path)
        try:
            server.serve(options.deploy_to)
        except ValueError, err:
            parser.error(err)
        
    
if __name__ == "__main__":
    main(sys.argv[1:])
    # cProfile.run('main(sys.argv[1:])', filename='hyde.cprof')
    # import pstats
    # stats = pstats.Stats('hyde.cprof')
    # stats.strip_dirs().sort_stats('time').print_stats(20)