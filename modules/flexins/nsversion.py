u"""Analysis and Check the FlexiNS software version.
"""
import re
from libs.checker import ResultInfo,CheckStatus
from libs.infocache import shareinfo
from libs.flexins import FlexiNS
from libs.tools import debugmsg

## Mandatory variables 
##--------------------------------------------
module_id = 'fnsbase.2016030500'
tag       = ['flexins','base']
priority  = 'normal'
name      = "Check the FNS software version"
desc      = __doc__
criteria  = "FNS package's ID match 'N5' or 'N4'"
result    = ResultInfo(name)


## Optional variables
##--------------------------------------------
target_version = ['N5 1.19-3','N5*']    
version_info = u"Packages Info:\n  %s"
check_commands = [
    ("ZWQO:CR;","show the NS packages information"),
]

##
def check_version(ns):
    error = ''
    info = []
    status = ''
        
    if ns and ns.get('version'):
        if ns.match_version(target_version):  # todo: match_version(BU=target_version)
            status = CheckStatus.PASSED
        else:
            status = CheckStatus.FAILED
        info.append(str(ns.version))
    #in case no ns version found.
    else:
        status = CheckStatus.UNKNOWN
        info.append("unknow version")
        error = " - Can't find the packages info from log."
    
    return status,info,error  
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    """The 'run' function is a mandatory fucntion. and it must return a ResultInfo.
    """
    
    ns = shareinfo.get('FlexiNS')
    debugmsg(shareinfo)
    status,info,error = check_version(ns)
    result.update(status=status,info=info,error=error)

    return result
    