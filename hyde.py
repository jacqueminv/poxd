#!/usr/bin/env python2
import os, sys
from optparse import OptionParser
from hyde import Generator
from hyde import Initializer
import cProfile

PROG_ROOT= os.path.dirname(os.path.abspath( __file__ ))

def main(argv):
    parser = OptionParser()
    parser.add_option("-s","--sitepath", dest="site_path")
    parser.add_option("-i","--init", action='store_true', dest="init", default=False)
    parser.add_option("-t","--template", dest="template")
    parser.add_option("-g","--generate", action="store_true", dest="generate", default=False)
    parser.add_option("-d","--deploy_to", dest="deploy_to")
    (options, args) = parser.parse_args()
    
    if len(args):
        parser.error("Unexpected arguments encountered.")
        
    if not options.site_path:
        options.site_path = os.getcwdu()
    
    if options.init:
        initializer = Initializer(options.site_path)
        try:
            initializer.initialize(PROG_ROOT, options.template)
        except ValueError, e:
            parser.error(e)
        
    if options.generate:
        generator = Generator(options.site_path)
        try:
            generator.generate(options.deploy_to)
        except ValueError, e:
            parser.error(e)
    
if __name__ == "__main__":
    main(sys.argv[1:])
    # cProfile.run('main(sys.argv[1:])', filename='hyde.cprof')
    # import pstats
    # stats = pstats.Stats('hyde.cprof')
    # stats.strip_dirs().sort_stats('time').print_stats(20)