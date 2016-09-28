#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Nokia Smart Elements Health Checker

this main program will import and run all the check modules listed in 
<checklist> file.

Usage:    
    smartchecker <checklist> [logfile|logdir] [options]

examples:
   smartchecker -s checklist.ckl
   smartchecker -r checklist.ckl logfile
   smartchecker -r checklist.ckl logfile  --saveto report_sae01.html
   smartchecker -r checklist.ckl logfile  --template bootstrap.html
"""
__programname__ = 'Smartchecker'
__version__     = '0.93'

import sys,os, argparse,time
import setsitenv
from libs.configobject import ConfigObject
from libs.checker import ImportCheckModules,ResultList,CheckList
from libs.reportor import CheckReport, get_builder
from libs.tools import MessageBuffer
from libs.infocache import shareinfo
from libs.logfile import LogFile, istextfile
from messagelogger import MessageLogger

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

SILENT          = False
REPORT_TEMPLATE = None


#initilize the logging.
logfile = CONFIG.get('checker_logfile','/tmp/smartchecker.log')
logging_level = CONFIG.get('logging_level','INFO')
rootlogger = MessageLogger()
#rootlogger.addFileHandler(logfile)
rootlogger.setLevel(logging_level)
logger = MessageLogger('SmartChecker')


def args_parse():
    global SILENT,REPORT_TEMPLATE
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
    parser.add_argument('-l','--log2file', action="store_true",
                        help="output the log info to file.")    
    parser.add_argument('-c','--commands',
                        help="generate the commands for collecting log.")

    args = parser.parse_args()

    if not (args.run or args.show):
        parser.print_help()
        sys.exit(1)

    if args.run and not args.logfile:
        print("Need to specify a log filename or directory!")
        sys.exit(1)

    DEBUG   = args.debug
    SILENT  = args.silent
    REPORT_TEMPLATE = args.template

    return parser, args

def save_output_to_file(report,filename,path=None):
    output_path = path or CONFIG.reports_path
    output_filename = os.path.join(output_path,filename)
    msgbuf = MessageBuffer()

    if isinstance(report,(str,unicode)):
        msgbuf.append(report)
        msgbuf.output('file',output_filename)
    else:
        report.save(output_filename)

def show_module_info(checklist,args):
    """show the information of given modules. if CONFIG.module_info_file is set,
    save the modules info to a file.
    parameters:
       checklist,   the CheckList object, contain the checklist info.
       logfile,     no use for this function.
    """

    msgbuf = MessageBuffer()
    cmdlist = []
    template = JinjaTemplate(CONFIG.template_path)

    if 'module_info' in checklist.templates:
        _template_file = args.template or checklist.templates['module_info']
        
    if not _template_file:
        template.load(CONFIG.show_modules_template)
    else:
        template.load(filename=_template_file)

    modules = checklist.modules

    for idx, m in enumerate(modules):
        if hasattr(m,'check_commands'):
            cmdlist.extend(m.check_commands)

    _info=template.render(**locals())
    msgbuf.append(_info)

    if not args.silent:
        msgbuf.output(CONFIG.runmode)
    
    if args.saveto:
        save_output_to_file(msgbuf,args.saveto)

    return 0

def check_logfile(checklist,logfile, report_name_tmpl=None):
    """run the check modules in console mode
    """
    log=LogFile(logfile)
    if not log.state or not log.match(checklist.netype):
        errmsg = "The %s does not match the element type in checklist:%s" % (logfile,checklist.netype)
        return None, errmsg

    results = ResultList()
    output_format = CONFIG.output_format
    errmsg = ""
    #msgbuf = MessageBuffer()    
    

    template_file = REPORT_TEMPLATE or checklist.templates['report']
    report_type = template_file.split('.')[-1]
    results.template_type = report_type

    report = CheckReport(template_path=CONFIG.template_path,
                         template_name=template_file,
                         output_path = CONFIG.get('report_path') or checklist.paths['reports'],
                         )

    report.add_data(checklist=checklist)
    report.get_builder(report_type)

    #print("Running check modules...")
    for idx,m in enumerate(checklist.modules):
        logger.info("Running the module: %s:%s" % (m.module_id,m.name))
        _result = m.run(logfile)
        _result.loadinfo(m)
        results.append(_result)

    report.add_data(results=results)
    element = shareinfo.get('ELEMENT')
    if not element:
        errmsg="No hostname and version info found in the log. quit."
        return None,errmsg
    report.add_data(element=element)

    report.add_data(hostname = element.hostname)
    report.add_data(timestamp = time.strftime("%Y-%m-%d %H:%M"))    

    if not report_name_tmpl:
        report_name_tmpl = "report_%(hostname)s.%(report_type)s"

    _filename = CONFIG.get('report_filename')
    report.output_filename = _filename or report_name_tmpl % locals()
    report.fill_data()
    saved_filename=report.save()
    logger.info("Save report to: %s" % saved_filename)


    results.hostname = report.get_data('hostname')
    results.report_filename = report.output_filename

    logger.info("Result: %s, Failed:%s, Unknow:%s, Passed:%s" % 
                (results.hostname,
                 results.stats_detail('FAILED'),
                 results.stats_detail('UNKNOWN'),
                 results.stats_detail('PASSED'),
                ))


    return results , errmsg


def check_logdir(checklist,logdir,output_path=''):
    resultlist = []
    errmsg = []

    for dirpath, _ ,files in os.walk(logdir):
        #change the path: /path/log/project/xxx to report_project_xxx
        cur_dirname = dirpath.replace(logdir,"report").strip(os.path.sep).replace(os.path.sep,'_')
        output_file_tmpl = "%s_%%(hostname)s.%%(template_type)s" % cur_dirname
        #print "SAVE OUTPUT2:", output_file_tmpl
        for fname in filter(istextfile, files):
            logfilename = os.path.join(dirpath,fname)
            logger.debug("checking the logfile:%s" % logfilename)
            result, _errmsg = check_logfile(checklist,logfilename, report_name_tmpl=output_file_tmpl)
            if result:
                logger.info("Analysising logfile: %s... SUCCESS!" % logfilename)
                resultlist.append(result)
            else:
                logger.info("Analysising logfile: %s...ERROR!" % logfilename)
                errmsg.append(_errmsg)
            
    return resultlist,errmsg

def check_log(checklist,logname):
    """Main entry to check the logfiles.
    """
    resultlist = []

    _reportpath =  checklist.paths['reports'] 

    logger.debug("The _reportpath is: %s" % _reportpath)

    #the given logname is a dir name.
    if os.path.isdir(logname):
        logger.debug("checking the log directory: %s" % logname)
        resultlist,errmsg = check_logdir(checklist,logname)
    else: #the logname is a filenameq
        logger.debug("checking the log file: %s" % logname)
        resultlist,errmsg = check_logfile(checklist,logname)

    if not resultlist and not errmsg:
        logger.error("No log file was found in the logfile directory: %s" % _reportpath)

    else:
        if isinstance(resultlist,list):
            reports_counter = len(resultlist)
        else:
            reports_counter = 1
        logger.info("Total %s reports were saved to path '%s'" % (reports_counter, _reportpath))

    logger.info("Checking finished.")

if __name__ == "__main__":   
    #parse the arguments and options.
    parser,args = args_parse()

    shareinfo.set('DEBUG',args.debug)
    if args.debug or logging_level=='DEBUG':
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')

    if args.log2file:
        _logfile = CONFIG.get('checker_logfile','/tmp/smartchecker.log')
        logger.addFileHandler(_logfile)

    logger.debug(args)
    CONFIG.logger = logger

    #checklsit was speicifiied. 
    checklist_file = args.run or args.show
    cklpath,cklfile = os.path.split(checklist_file)
    
    #load the checklist file.
    if not cklpath:
        cklpath = CONFIG.checklist_path
    checklist = CheckList(os.path.join(cklpath,cklfile))

    #determinate the output path and filename.
    if args.saveto:
        _path,_filename = os.path.split(args.saveto)
        CONFIG.report_filename = _filename
        CONFIG.report_path = _path or checklist.paths['reports']


    #import the modules and save to checklist.modules 
    checklist.modules = ImportCheckModules(checklist)

    if not checklist.modules:
        parser.print_help()
        sys.exit(1)

    if args.run:
        check_log(checklist,args.logfile)
    elif args.show:
        show_module_info(checklist,args)