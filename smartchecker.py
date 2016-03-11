# -*- coding: utf-8 -*-
"""Nokia Smart NE Health Checker

SmartChecker will import and run all the health check modules listed in 
<checklist_options> or default modules directory:<modules>

Usage: 
    
    smartchecker [logfile] [checklist_options]

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
__programname__ = 'Smartchecker'
__version__     = '0.613'

import sys,os, argparse
from libs.configobject import ConfigObject
from libs.checker import ImportCheckModules,ResultList
from libs.tools import OutputBuffer

default_config = {
'output_format' : "reading",
'modules_path'  : "modules",
'runmode'       : "console",
}

## initilize the global variables with default config.
CONFIG = ConfigObject(default_config)

## load the variables from config file.
config_file = 'checker.conf'
if os.path.exists(config_file):  #read the config file if it's exists.
    CONFIG.read(config_file)

DEBUG = False

def args_parse():
    parser = argparse.ArgumentParser(version=" v".join([__programname__,__version__]))
    
    parser.usage = __doc__
 
    parser.add_argument('logfile', nargs='?',
                        help="specify the log file.")
    parser.add_argument('-r','--run',
                        help="run the modules specified in check lsit. ")
    parser.add_argument('-s','--show',
                        help="view the modules specified in check lsit.")    
    parser.add_argument('-d','--debug', action="store_true",
                        help="debug option, detail info will be output")

    return parser,parser.parse_args()

def command_description(cmdlist):
    """ combine every command and its description in the <cmdlist> to two line string.
    this function is for output the check commands.
    """
    #cmdmark = "#CmdMark#"
    cmd_desc_format ="\n## %(desc)s \n%(cmd)s\n"

    _cmdstr = []
    for cmd,desc in cmdlist:
        _cmdstr.append(cmd_desc_format % dict(desc=desc.capitalize(),cmd=cmd))
    
    return _cmdstr


def show_module_info(modules,logfile=None):
    """show the information of given modules """

    _hashline = "#" * 68
    outbuf = OutputBuffer()
    cmdlist = []

    for m in modules:
        outbuf.append("- name: %s\n  desc: %s\n" % (m.name,m.desc))
        if hasattr(m,'check_commands'):
            cmdbuf="".join(command_description(m.check_commands))
            #outbuf.append("- check commands:\n%s\n" % cmdbuf)
            cmdlist.append(cmdbuf)

    outbuf.append("There are total %s check modules need to been run." % len(modules))
    outbuf.append("\n\n"+ _hashline)
    outbuf.append("\n# Below are all the commands used to collect the needed information:")
    outbuf.append("\n"+ _hashline)
    outbuf.append("".join(cmdlist))
    outbuf.output(CONFIG.runmode)

    return 0

def run_modules(modules,logfile):
    """run the check modules in console mode
    """
    results = ResultList()
    output_format = CONFIG.output_format
    err_flag = 0

    print("Running check modules...")
    #print "ModuleName\t Result\t Description"
    #print "-"*50    
    for idx,m in enumerate(modules):
        _result = m.run(logfile)
        status_str = "\n[%s] %s: " % (idx+1, m.name if isinstance(m.name, unicode) else unicode(m.name, "utf-8"))
        criteria_str = "Criteria: %s" % (m.criteria if isinstance(m.criteria, unicode) else unicode(m.criteria, "utf-8"))
        print(status_str)
        print(criteria_str)
        _result.dump(output_format)        
        results.append(_result)
        #results.append(m.run(CONFIG.logfile))

    print("\nTotal %s check modules were executed." % len(results))
    #print results.stats()
    for key,value in results.stats().items():
        print("%10s: %s" % (key,value))

    #no error happend, 0 is return.
    return err_flag

if __name__ == "__main__":

    do_action = {'show' : show_module_info,
                 'run'  : run_modules,
                }

    parser,args = args_parse()
    DEBUG = args.debug

    if DEBUG:
        print(args)

    #print(CONFIG)
    modules_list = args.run or args.show
    modules = []
    modulepath,modulefile = os.path.split(modules_list)
    if not modulepath:
        modulepath = CONFIG.checklist_path

    modules = ImportCheckModules(os.path.join(modulepath,modulefile))

    if not modules:
        parser.print_help()
        sys.exit(1)

    command = (args.run and 'run') or (args.show and 'show') or 'run'

    sys.exit(do_action[command](modules,args.logfile))
