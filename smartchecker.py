#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Nokia Smart Elements Health Checker

SmartChecker will import and run all the health check modules listed in <checklist> file.

Usage:    
    smartchecker <checklist> [logfile]

examples:
   smartchecker -s checklist.ckl
   smartchecker -r checklist.ckl logfile   
   smartchecker -r checklist.ckl logfile  --saveto report_sae01.html
   smartchecker -r checklist.ckl logfile  --saveto report_sae01.html --silent
"""
__programname__ = 'Smartchecker'
__version__     = '0.9'

import sys,os, argparse,time,re
from libs.configobject import ConfigObject
from libs.checker import ImportCheckModules,ResultList,CheckList
from libs.reportor import CheckReport, JinjaTemplate
from libs.tools import MessageBuffer,debugmsg
from libs.infocache import shareinfo
from libs.logfile import LogFile

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

DEBUG    = False
SILENT   = False
REPORT_TEMPLATE = None
SAVE_OUTPUT = None

def args_parse():
    global DEBUG,SILENT,REPORT_TEMPLATE,SAVE_OUTPUT
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
    parser.add_argument('--saveto', 
                        help="save the report to a specified filename ")
    parser.add_argument('--silent', action="store_true",
                        help="turn off the output to stdout.")    
    parser.add_argument('-t','--template',
                        help="template for report output.")
    parser.add_argument('-c','--commands',
                        help="template for report output.")

    args = parser.parse_args()

    if not (args.run or args.show):
        parser.print_help()
        sys.exit(1)

    if args.run and not args.logfile:
        print("Need to specify a logfile!")
        sys.exit(1)

    DEBUG   = args.debug
    SILENT  = args.silent
    REPORT_TEMPLATE = args.template
    SAVE_OUTPUT     = args.saveto

    return parser, args

def save_output_to_file(msgbuf,filename,path=None):
    output_path = path or CONFIG.reports_path
    msgbuf.output('file',os.path.join(output_path,filename))

def show_module_info(checklist,logfile=None):
    """show the information of given modules. if CONFIG.module_info_file is set,
    save the modules info to a file.
    parameters:
       checklist,   the CheckList object, contain the checklist info.
       logfile,     no use for this function.
    """

    msgbuf = MessageBuffer()
    cmdlist = []
    jinja = JinjaTemplate(CONFIG.template_path)

    if 'module_info' in checklist.templates:
        template = jinja.template(checklist.templates['module_info'])
    else:
        template = jinja.template()(CONFIG.show_modules_template)


    modules = checklist.modules

    for idx, m in enumerate(modules):
        if hasattr(m,'check_commands'):
            cmdlist.extend(m.check_commands)

    #info=template.render(modules=modules,cmdlist=cmdlist,checklist=checklist)
    info=template.render(locals())
    msgbuf.append(info)

    if not SILENT:
        msgbuf.output(CONFIG.runmode)
    
    if SAVE_OUTPUT:
        save_output_to_file(msgbuf,SAVE_OUTPUT)

    return 0

def check_logfile(checklist,logfile):
    """run the check modules in console mode
    """
    log=LogFile(logfile)
    if not log.match(checklist.netype):
        errmsg = "The %s does not match the element type in checklist:%s" % (logfile,checklist.netype)
        return None, errmsg

    results = ResultList()
    output_format = CONFIG.output_format
    errmsg = ""
    jinja = JinjaTemplate(CONFIG.template_path)

    template_file = REPORT_TEMPLATE or checklist.templates['report']
    template_type = template_file.split('.')[-1]
    template = jinja.template(template_file)
    msgbuf = MessageBuffer()

    report = CheckReport()
    report.template_path = CONFIG.template_path
    report.template_name = checklist.templates['report']

    results.template_type = template_type
    
    #print("Running check modules...")
    for idx,m in enumerate(checklist.modules):
        _result = m.run(logfile)
        _result.criteria = m.criteria    
        results.append(_result)

    timestamp=time.strftime("%Y-%m-%d %H:%M")
    element = shareinfo.get('ELEMENT')
    if not element:
        errmsg="No hostname and version info found in the log. quit."
        return None,errmsg

    hostname = element.hostname
    label_state = {'critical':'danger','major':'warning','normal':'info','default':'default'}  
    _report = template.render(locals())
    msgbuf.append(_report)

    if not SILENT and template_type =='md':
        msgbuf.output(CONFIG.runmode)

    if SAVE_OUTPUT:
        report_filename = SAVE_OUTPUT % locals()
        save_output_to_file(msgbuf,report_filename)
    else:
        report_filename = '.'.join((hostname,template_type))
        save_output_to_file(msgbuf,report_filename)

    results.report_filename = report_filename

    return results , errmsg


def check_logdir(checklist,logdir):
    global SAVE_OUTPUT
    resultlist = []
    errmsg = []
    for dirpath, _ ,files in os.walk(logdir):
        #change the path: /path/log/project/xxx to project_xxx
        cur_dirname = dirpath.replace(logdir,"").strip(os.path.sep).replace(os.path.sep,'_')
        SAVE_OUTPUT = "%s_%%(hostname)s.%%(template_type)s" % cur_dirname
        for fname in files:
            filename = os.path.join(dirpath,fname)
            print "Analysising logfile: %s..." % filename,
            result, _errmsg = check_logfile(checklist,filename)
            if result:
                print("SUCCESS!") 
                print("Save report to: %s" % result.report_filename)
                resultlist.append(result)
            else:
                print("ERROR!")
                errmsg.append(_errmsg)
            print 

    return resultlist,errmsg

def check_log(checklist,logname):
    resultlist = []
    #the given logname is a dir
    if os.path.isdir(logname):
        resultlist,errmsg = check_logdir(checklist,logname)
    else:
        resultlist,errmsg = check_logfile(checklist,logname)

    if not resultlist:
        print "\nERROR: %s" % errmsg
    else:
        print "\nSave the %s success report to path '%s'" % (len(resultlist),checklist.paths['reports'])

if __name__ == "__main__":

    do_action = {'show'     : show_module_info,
                 'run'      : check_log,
                }
    
    #parse the arguments and options.
    parser,args = args_parse()
    shareinfo.set('DEBUG',args.debug)
    debugmsg(args)

    #checklsit was speicifiied. 
    checklist_file = args.run or args.show
    cklpath,cklfile = os.path.split(checklist_file)
    
    #load the checklist file.
    if not cklpath:
        cklpath = CONFIG.checklist_path
    checklist = CheckList(os.path.join(cklpath,cklfile))

    #import the modules and save to checklist.modules 
    checklist.modules = ImportCheckModules(checklist)

    if not checklist.modules:
        parser.print_help()
        sys.exit(1)

    command = (args.run and 'run') or (args.show and 'show') or 'run'
    do_action[command](checklist,args.logfile)
