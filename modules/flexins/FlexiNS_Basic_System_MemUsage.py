# -*- coding: utf-8 -*-
u"""
检查FlexiNS 内存利用率
  - 检查指令:
      ZDOI::M;

    该指令列出当前各单元的内存使用状态。
"""

import re,sys,time
from libs.checker import ResultInfo
from libs.checker import CheckStatus
from libs.infocache import shareinfo
from libs.log_spliter import LogSpliter ,LOG_TYPE_FLEXI_NS

__author__ = 'liming.wang'
__email__  = 'liming.wang@nokia.com'
__date__   = '2016-07-28'

## Mandatory variables
##--------------------------------------------
#module_id = 'NSTCN_20160729'
module_id = 'FlexiNS_Basic_System_MemUsage'
tags      = ['china', 'flexins']
priority  = 'minor'
name      = u"FlexiNS 内存利用率"
desc      = __doc__
criteria  = u"""
（1）检查MME内存利用率是否超过70%。

"""
LIMIT=80

result = ResultInfo(name,module_id=module_id,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['N5', 'N6']

##在这里添加获取所需log的命令
check_commands = [
    ("ZDOI::M;","show the NS memory usage")
]
patten = re.compile("^[0-9,A-F]{4} [0-9,A-F]{2} [0-9,A-F]{4}")
info = " %s memory usage: %s, Check status: %s"
### below add the optional functions for checking

#
# 在这里添加检查的辅助子程序
#
def read_block(logfile,blkname):
    logspliter=LogSpliter(type=LOG_TYPE_FLEXI_NS)
    logspliter.load(logfile)
    return logspliter.get_log(blkname,fuzzy=True)



##--------------------------------------------
## Mandatory function: run
##--------------------------------------------
def run(logfile):
    rsult_info = []
    status_info = [CheckStatus.UNKNOWN]

    blocks = read_block(logfile, 'ZDOI::M;')

    for block in blocks:
        status = CheckStatus.UNCHECKED
        for line in list(block.result):
            line = line.strip()
            if (re.match("UNIT:",line)):
                fields = line.split(':')
                unit=fields[1].strip()
            if (re.match("FREE MEMORY",line)):
                fields = line[36:].strip()
                freemem=int(fields)
                mem_usage=100-freemem
                if mem_usage<LIMIT:
                    status=CheckStatus.PASSED
                else:
                    status=CheckStatus.FAILED
                status_info.append(status)

                rsult_info.append(info % (unit, mem_usage,status))
    del(status_info[0])
    total_status=CheckStatus.FAILED
    if len(status_info)==0:
        error = "Can't find unit load in this log!"
    elif status_info.count(CheckStatus.FAILED)>0:
        error="Check Failed!"
    else:
        error = ''
        total_status=CheckStatus.PASSED

    result.update(status=total_status, info=rsult_info, error=error)

    return result