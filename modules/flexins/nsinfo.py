u"""Collecting the basic info of FlexiNS.
"""

from libs.checker import ResultInfo,CheckStatus
from libs.infocache import InfoCache
from libs.flexins import FlexiNS

## Mandatory variables 
##--------------------------------------------
module_id = 'fnsbase.nsinfo'
tag       = ['flexins','base']
priority  = 'default'
name      = "FlexiNS basic info collecting"
desc      = __doc__
criteria  = "FNS basic info collecting."
result    = ResultInfo(name,priority=priority)


## Optional variables
##--------------------------------------------
check_commands = [
    ("ZWQO:CR;","show the NS packages information"),
    ("ZQNI:;","show the NS O&M configuratio"),  
]
shareinfo = InfoCache()
info_template="""FlexiNS Info:
 - hostname: %(hostname)s
 -  version: %(version)s
 -    C-NUM: %(c_num)s
 -localtion: %(location)s
 - hardware: 
"""
##

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    """The 'run' function is a mandatory fucntion. and it must return a ResultInfo.
    """
    errmsg = ""

    ns = FlexiNS(logfile=logfile)
    if ns.hostname == "UNKNOWN" and not hasattr(ns,'version'):
        print "Can't find the host info in log"
        exit(1)

    shareinfo.set('ELEMENT',ns)
    status = CheckStatus.PASSED
    info = info_template % ns._data

    result.update(status=status,info=[info],error=errmsg)
    return result
    