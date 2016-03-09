"""Analysis and Check the FlexiNS software version.

"""
import re
from libs.checker import ResultInfo,CheckStatus
from libs.log_spliter import LogSpliter,LOG_TYPE_FLEXI_NS
from libs.tools import read_cmdblock_from_log

## Mandatory variables 
##--------------------------------------------
module_id = 'fnsbase.20160305.01'
tag       = ['flexins','base']
priority  = 'normal'
name      = "Check the FNS software version"
desc      = __doc__
criteria  = "FNS version is ['N5 1.19-3']."
result    = ResultInfo(name)
##--------------------------------------------

## Optional variables
##--------------------------------------------
target_version = ['N5 1.19-3']    
version_info = "Packages Info:\n  %s"
pat_pkgid= re.compile("\s+(BU|FB|NW)\s+.*?\n\s+(\w\d [\d\.-]+)")
check_commands = [
    ("ZWQO:CR;","show the NS packages information"),
]
##
def check_version(logtxt):
    error = ''
    info = ''
    status = ''

    pkgid = dict(pat_pkgid.findall(str(logtxt)))

    try:
        if pkgid['BU'] in target_version:
            status = CheckStatus.PASSED
        else:
            status = CheckStatus.FAILED
        info = str(pkgid)
    except (KeyError,ValueError) as e:
        status = CheckStatus.UNKNOWN
        info = e  
    
    return status,info,error  
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    """The 'run' function is a mandatory fucntion. and it must return a ResultInfo.
    """
    ns_command_end_mark = "COMMAND EXECUTED"  
    logtxt = read_cmdblock_from_log(logfile,'ZWQO:CR;',ns_command_end_mark)
    if logtxt:
        status,info,error = check_version(logtxt)
        result.update(status=status,info=(version_info % info).split('\n'),error=error)
    else:
        status = CheckStatus.UNKNOWN
        error = "Can't find the version info in the log."
        result.update(status=status,info='',error=error)
    
    return result
    