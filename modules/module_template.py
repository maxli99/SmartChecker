# -*- coding: utf-8 -*-
u"""
{{description}}
"""

import re,sys
from libs.checker import ResultInfo
from libs.checker import CheckStatus
from libs.infocache import shareinfo
from libs.log_spliter import LogSpliter

## Mandatory variables 
##--------------------------------------------
module_id = '{{module_id}}'
tags      = {{tags}}
priority  = '{{priority or 'major'}}'
name      = u"{{name}}"
desc      = __doc__
criteria  = u"""
{{criteria}}
"""
result = ResultInfo(name,module_id=module_id,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = {{target_version}}  

##在这里添加获取所需log的命令
check_commands = [
    #("ZWQO:CR;","show the NS packages information"),
    #('ZDDE:{@UNIT_ID}:"cat /proc/cpuinfo | grep processor",;',"show CPU info of all CPU blade"),
]

### below add the optional functions for checking

#
# 在这里添加检查的辅助子程序
#

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    status = CheckStatus.UNCHECKED 
    errmsg = []    
    
    ne = shareinfo.get('ELEMENT')
    # Check network element's Version
    vstatus,msg = ne.version_in_list(target_version)
    
    ##无法获得版本信息
    if vstatus == CheckStatus.VERSION_UNKNOWN:
        result.update(status=CheckStatus.UNKNOWN,info=[msg],error=error)
    
    ##网元版本符合条件
    elif vstatus== CheckStatus.VERSION_MATCHED:
        #
        # 在这里运行检查的内容
        #   
        result.update(status=status,info=_msg,error=errmsg)
   
    ##网元版本不符合条件
    elif vstatus == CheckStatus.VERSION_UNMATCHED:
        result.update(status=CheckStatus.PASSED,info=[msg],error=errmsg)
    
    return result
