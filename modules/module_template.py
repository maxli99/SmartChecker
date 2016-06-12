# -*- coding: utf-8 -*-
u"""Module Description

"""

import re,sys
from libs.checker import ResultInfo
from libs.checker import CheckStatus
from libs.infocache import shareinfo
from libs.log_spliter import LogSpliter

## Mandatory variables 
##--------------------------------------------
module_id = '{{module.id}}'
tag       = ['china',{{module.type}}]
priority  = '{{module.priority}}'
name      = u"{{module.name}}"
desc      = __doc__
criteria  = u"""描述检查的条件和标准

"""
result = ResultInfo(name,module_id=module_id,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['N5','N6']    

check_commands = [
    ##此次添加收集log的相关命令。格式：(命令,  注释说明)
    ("ZWQO:CR;", "show the NS packages information"),
    ('ZDDE:{@UNIT_ID}:"cat /proc/cpuinfo | grep processor",;',"show CPU info of all CPU blade"),
]
def process_num(block):
    num = 0
    pat = re.compile("processor")
    _processors=re.findall("processor\s+: \d{1,2}",''.join(block))
    
    return len(_processors)
     
def caculate_cpu_cores(logfile):
    log=LogSpliter(logfile=logfile)
    #log.load(logfile)
    unit_pat = re.compile("ZDDE:(\w+),(\d+)")
    
    core_nums = {}
    for blk in log.get_log("cpuinfo",fuzzy=True):
        _unit = unit_pat.findall(blk.command)
        if _unit:
            unit = "-".join(_unit[0])
        else:
            continue
        core_nums[unit] = process_num(blk.result)
        
    return core_nums


##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    status = CheckStatus.UNCHECKED 
    errmsg = []    
    
    ns = shareinfo.get('ELEMENT')
    # Check NS Version
    vstatus,msg = ns.version_in_list(target_version)

    if vstatus == CheckStatus.VERSION_UNKNOWN:
        result.update(status=CheckStatus.UNKNOWN,info=[msg],error=error)
    
    elif vstatus== CheckStatus.VERSION_MATCHED:
        cpuinfo = caculate_cpu_cores(logfile)
        _msg = []

        for unit,corenum in cpuinfo.items():
            if corenum < 12:
                errmsg.append("- Blade %s only have %s cores, Some cores are missing. 部分核丢失" % (unit,corenum))
            else:
                _msg.append("- Blade %s have 12 cores" % unit)
                
        if len(errmsg) > 0:
            status=CheckStatus.FAILED
        else:
            status=CheckStatus.PASSED
            
        result.update(status=status,info=_msg,error=errmsg)
   
    elif vstatus == CheckStatus.VERSION_UNMATCHED:
        result.update(status=CheckStatus.PASSED,info=[msg],error=errmsg)
    
    return result
