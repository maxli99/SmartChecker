u"""Collecting the basic info of FlexiNS.
"""

from libs.checker import ResultInfo,CheckStatus
from libs.infocache import InfoCache
from libs.tools import debugmsg
from libs.flexing import FlexiNG

## Mandatory variables 
##--------------------------------------------
module_id = 'fngbase.2016030500'
tag       = ['flexins','base']
priority  = 'normal'
name      = "FlexiNG basic info collecting"
desc      = __doc__
criteria  = "FNG basic info collecting."
result    = ResultInfo(name)


## Optional variables
##--------------------------------------------
check_commands = [
    ('#'*60,"Please use `ngexec` to execute below commands:"),
    ('@bash\nldapsearch "fsLogicalNetworkElemId=*"',"list the hostname & version info. must be run in shell mode not fsclish"),
]
shareinfo = InfoCache()
DEBUG = shareinfo.get('DEBUG')
info_template="""FlexiNG Info:
 - hostname: %(hostname)s
 -  version: %(version)s
 - hardware: AB%(hardware)s
"""
##

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    """The 'run' function is a mandatory fucntion. and it must return a ResultInfo.
    """
    info = []
    ng = FlexiNG(logfile=logfile)  
    #ng.parse_log(logfile)

    shareinfo.set('ELEMENT',ng)
    
    _data = ng._data.copy()
    _data['hardware'] = ng.version.get('hardware','?')
    info.append(info_template % _data)
    result.update(status=CheckStatus.PASSED,info=info,errmsg="")
   
    return result
    