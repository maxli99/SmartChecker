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
from libs.checker import ImportCheckModules,ResultList,CheckList
from libs.reportor import Reportor, JinjaTemplate
from libs.tools import MessageBuffer

default_config = {
'output_format' : "reading",
'modules_path'  : "modules",
'runmode'       : "console",
}

module_info_format ="""
Module #{{idx}}
----------------------------------------------------------------
       Name: {{module.name}}
Description: {{module.desc}}
"""
## initilize the global variables with default config.
CONFIG = ConfigObject(default_config)

## load the variables from config file.
config_file = 'checker.conf'
if os.path.exists(config_file):  #read the config file if it's exists.
    CONFIG.read(config_file)

DEBUG = False
SAVEFILE = False

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
    parser.add_argument('--save', action="store_true",
                        help="save the module info if option is set. ")

    return parser,parser.parse_args()

def command_description(cmdlist):
    """Combine every command and its description in the <cmdlist> to two line string.
This function is used to output the check commands for log collections.
    """
    #cmdmark = "#CmdMark#"
    cmd_desc_format ="\n## %(desc)s \n%(cmd)s\n"

    _cmdstr = []
    for cmd,desc in cmdlist:
        _cmdstr.append(cmd_desc_format % dict(desc=desc.capitalize(),cmd=cmd))
    
    return _cmdstr


def show_module_info(checklist,logfile=None):
    """show the information of given modules """

    msgbuf = MessageBuffer()
    cmdlist = []
    jinja = JinjaTemplate(CONFIG.template_path)

    if 'module_info' in checklist.templates:
        template = jinja.template(checklist.templates['module_info'])
    else:
        template = jinja.template()(module_info_format)


    modules = checklist.modules

    for idx, m in enumerate(modules):
        #print "type:",type(m.name),type(m.desc),type(m.criteria)
        infotext = template.render(idx=idx+1,module=m)
        msgbuf.append(infotext)
        if hasattr(m,'check_commands'):
            cmdbuf="".join(command_description(m.check_commands))
            cmdlist.append(cmdbuf)

    msgbuf.append("\n##The Checklist include below %s check modules:\n" % len(modules))

    msgbuf.append("\n# Below are all the commands used to collect the needed information:")
    msgbuf.append("="*70+"\n")    
    msgbuf.append("".join(cmdlist))

    msgbuf.output(CONFIG.runmode)
    if CONFIG.get('module_info_file'):
        msgbuf.output('file',CONFIG.get('module_info_file'))
    return 0

def run_modules(checklist,logfile):
    """run the check modules in console mode
    """
    results = ResultList()
    output_format = CONFIG.output_format
    err_flag = 0
    jinja = JinjaTemplate(CONFIG.template_path)
    template = jinja.template(checklist.templates['report'])
    msgbuf = MessageBuffer()

    print("Running check modules...")
  
    for idx,m in enumerate(checklist.modules):
        _result = m.run(logfile)
        _result.criteria = m.criteria    
        results.append(_result)
        #results.append(m.run(CONFIG.logfile))

    report = template.render(results=results)
    print type(report)
    print(report)

    # print("\nTotal %s check modules were executed." % len(results))
    # #print results.stats()
    # for key,value in results.stats().items():
    #     print("%10s: %s" % (key,value))

    # if checklist.templates['report']:
    #     #print "templatefile:",templatefile
    #     report = Reportor(checklist.templates['report'])
    #     report.load_data(results)
    #     report.save()

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
    checklist_file = args.run or args.show
    cklpath,cklfile = os.path.split(checklist_file)
    
    if not cklpath:
        cklpath = CONFIG.checklist_path

    checklist = CheckList(os.path.join(cklpath,cklfile))
    checklist.import_modules()
    if args.save:
        CONFIG.set('module_info_file',checklist.templates['module_info'])
    if not checklist.modules:
        parser.print_help()
        sys.exit(1)

    command = (args.run and 'run') or (args.show and 'show') or 'run'

    do_action[command](checklist,args.logfile)
