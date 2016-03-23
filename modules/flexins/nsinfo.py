u"""Collecting the basic info of FlexiNS.
"""

from libs.checker import ResultInfo,CheckStatus
from libs.tools import InfoCache
from libs.flexins import FlexiNS

## Mandatory variables 
##--------------------------------------------
module_id = 'fnsbase.2016030500'
tag       = ['flexins','base']
priority  = 'normal'
name      = "FlexiNS basic info collecting"
desc      = __doc__
criteria  = "FNS basic info collecting."
result    = ResultInfo(name)


## Optional variables
##--------------------------------------------
check_commands = [
    ("ZWQO:CR;","show the NS packages information"),
]
shareinfo = InfoCache()
info_template="""FlexiNS Info:
 - hostname: %(hostname)s
 -  version: %(version)s
 - hardware: 
"""
##

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    """The 'run' function is a mandatory fucntion. and it must return a ResultInfo.
    """

    ns = FlexiNS()  
    ns.parse_log(logfile)
       
    shareinfo.set('FlexiNS',ns)
    
    result.status = CheckStatus.PASSED
    result.info = info_template % ns._data
    result.errmsg = ""
    
    return result
    