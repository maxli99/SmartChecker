# -*- coding: utf-8 -*-
u"""Collecting the basic info of FlexiNS.
"""

from libs.checker import ResultInfo,CheckStatus
from libs.infocache import InfoCache
from libs.flexing import FlexiNG

## Mandatory variables 
##--------------------------------------------
module_id = 'fngbase.2016030500'
tag       = ['flexins','base']
priority  = 'default'   # default,normal,major,critical
name      = "FlexiNG basic configuration and info collecting"
desc      = __doc__
criteria  = "Configurations were recognized successfully."
result    = ResultInfo(name)


## Optional variables
##--------------------------------------------
check_commands = [
    ('#'*60,"Please use `ngexec` to execute below commands:"),
    ('@bash\nldapsearch "fsLogicalNetworkElemId=*"',"list the hostname & version info. must be run in shell mode not fsclish"),
    ('@fsclish',"#switch to fsclish commands"),
    ("show config fsClusterId=ClusterRoot fsFragmentId=FlexiNG fsFragmentId=Internal","#show Hicut configuration"),
]
##shareinfo的信息可以在所有检查模块内共享
shareinfo = InfoCache()
DEBUG = shareinfo.get('DEBUG')
#用于输出附加信息的模板
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
    #附加信息内容
    info = []
    #检查的结果状态
    status = CheckStatus.PASSED
    #错误信息
    errmsg = []
    
    ng = FlexiNG(logfile=logfile)
    if ng.hostname == "UNKNOWN" or (not ng.version):
        status = CheckStatus.UNKNOWN
        info.append("can't determinate the hostname or version. 无法判断主机名或版本信息\n")
        
    shareinfo.set('ELEMENT',ng)
    
    _data = ng._data.copy()
    _data['hardware'] = ng.version.get('hardware','?')
    info.append(info_template % _data)
    result.update(status=status,info=info,errmsg="".join(errmsg))
   
    return result
    