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
priority  = 'default'   # default,normal,major,critical
name      = "FlexiNG basic configuration and info collecting"
desc      = __doc__
criteria  = "Configurations were recognized successfully."
result    = ResultInfo(name,priority=priority)


## Optional variables
##--------------------------------------------
check_commands = [
    ('#'*60,"Please use `ngexec` to execute below commands:"),
    ('@bash\nldapsearch "fsLogicalNetworkElemId=*"',"list the hostname & version info. must be run in shell mode not fsclish"),
    ('@fsclish',"#switch to fsclish commands"),
    ("show config fsClusterId=ClusterRoot fsFragmentId=FlexiNG fsFragmentId=Internal","#show Hicut configuration"),
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
    if ng.hostname == "UNKNOWN" and not hasattr(ng,'version'):
        print "Can't find the host info in log"
        exit(1)

    shareinfo.set('ELEMENT',ng)
    
    _data = ng._data.copy()
    _data['hardware'] = ng.version.get('hardware','?')
    info.append(info_template % _data)
    result.update(status=CheckStatus.PASSED,info=info,errmsg="")
   
    return result
    