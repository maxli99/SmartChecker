# -*- coding: utf-8 -*-
"""Nokia Smart NE Health Checker
  
  smartchecker [logfile] [checklist_options]

SmartChecker will import and run all the health check modules listed in 
<checklist_options> or default modules directory:<modules>

Checklist options:
	-s, --show	show all check modules information.
	-r, --run 	run all check scripts/rules under directory 'modules' if no check modules 
                list specified.

logfile:
	the logfile to be analysised and checked.

examples:

   smartchecker logfile  -r check.list
   smartchecker -s check.list
   smartchecker logfile
"""
__programname__ = 'smartchecker'
__version__     = '0.611'

import sys,os, argparse
from libs.configobject import ConfigObject
from libs.checker import ImportCheckModules,ResultList

## load the configuration file. Global Variables
CONFIG_FILE = 'checker.conf'
if os.path.exists(CONFIG_FILE):  #read the config file if it's exists.
    CONFIG = ConfigObject(CONFIG_FILE)
else:       #set the default options if config file doesn't exists.
    CONFIG = ConfigObject()
    CONFIG.output_format = "reading"
    CONFIG.default_modules_path = "modules"

DEBUG = False

def args_parse():
    parser = argparse.ArgumentParser(version=" v".join([__programname__,__version__]))
    
    parser.usage = __doc__
 
    parser.add_argument('logfile', nargs='?',
                        help="specify the FlexiNG configration file.")
    parser.add_argument('-r','--run',
                        help="run the modules specified in check lsit. default is all modules in directory:'modules/'")
    parser.add_argument('-s','--show',
                        help="view the modules specified in check lsit. default is all modules in directory:'modules/'")    
    parser.add_argument('-d','--debug', action="store_true",
                        help="debug option, detail info will be output")

    return parser,parser.parse_args()

def list_modules(modules,logfile=None):
    """list the information of all script modules """

    for m in modules:
        print("- name: %s\n  desc: %s\n" % (m.name,m.desc))

    print("There are total %s check modules need to been run." % len(modules))

    return 0

def run_modules(modules,logfile):
    """run the check modules 
    """
    results = ResultList()
    output_format = CONFIG.output_format

    print "Running check modules..."
    #print "ModuleName\t Result\t Description"
    #print "-"*50    
    for idx,m in enumerate(modules):
        rslt = m.run(logfile)
        status_str = "\n[%s] %s: " % (idx+1,m.name)
        criteria_str = "Criteria: %s" % m.criteria
        print status_str
        print criteria_str
        rslt.dump(output_format)        
        results.append(rslt)
        #results.append(m.run(CONFIG.logfile))

    print "\nTotal %s check modules were executed." % len(results)
    #print results.stats()
    for key,value in results.stats().items():
        print "%10s: %s" % (key,value)

    return

if __name__ == "__main__":

    do_action = {'show' : list_modules,
                 'run'  : run_modules,
                }

    parser,args = args_parse()
    DEBUG = args.debug

    if DEBUG:
        print args

    modules_list = args.run or args.show
    modules = []
    if modules_list:
        modules = ImportCheckModules(modules_list)
    if not modules:
        parser.print_help()
        sys.exit(1)

    command = (args.run and 'run') or (args.show and 'show') or 'run'

    sys.exit(do_action[command](modules,args.logfile))
