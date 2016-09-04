# -*- coding: utf-8 -*-
u"""
检查FlexiNG CPU 负荷
  - 检查指令:
      show ng-admin host-commands fastpath-cpu-load node-name

    该指令列出当前各单元的内存使用状态。
"""

import re,sys,time
from libs.checker import ResultInfo
from libs.checker import CheckStatus
from libs.infocache import shareinfo
from libs.log_spliter import LogSpliter,LOG_TYPE_FLEXI_NG


__author__ = 'liming.wang'
__email__  = 'liming.wang@nokia.com'
__date__   = '2016-08-29'

## Mandatory variables
##--------------------------------------------
#module_id = 'NSTCN_20160729'
module_id = 'FlexiNG_Basic_System_CpuLoad'
tags      = ['china', 'flexing']
priority  = 'minor'
name      = u"FlexiNG CPU 负荷"
desc      = __doc__
criteria  = u"""
（1）检查FlexiNG CPU 负荷是否超过70%。
"""
LIMIT=70

result = ResultInfo(name, module_id=module_id, priority=priority)
error = ''


##--------------------------------------------
## Optional variables
#target_version = ['N5', 'N6']
pat_list = {'unitname': re.compile(r".*show ng-admin host-commands fastpath-cpu-load node-name (\w+-\d+)"),
        'cpuload': re.compile(r"fp_cpu_load ="),
}

##在这里添加获取所需log的命令
check_commands = [
    ("show ng-admin host-commands fastpath-cpu-load node-name", "show the NG CPU load")
]
#patten = re.compile("^[0-9,A-F]{4} [0-9,A-F]{2} [0-9,A-F]{4}")
info = " %s cpu load: %s, Check status: %s"
### below add the optional functions for checking

#
# 在这里添加检查的辅助子程序
#


def read_block(logfile,blkname):
   pass


##--------------------------------------------
## Mandatory function: run
##--------------------------------------------

def run(logfile):
    rsult_info = []
    status_info = []
    status = CheckStatus.UNCHECKED

    with open(logfile,'r') as f:
        line=f.readline().strip()
        unit=''
        while line:
            r=pat_list['unitname'].match(line)
            if r:
                unit=r.group(1)
            r=pat_list['cpuload'].match(line)
            if r:
                unit_load=line.split("=")[1].strip()
                if int(unit_load)<LIMIT:
                    status=CheckStatus.PASSED
                else:
                    status=CheckStatus.FAILED
                status_info.append(status)
                if unit:
                    rsult_info.append(info % (unit, unit_load,status))
            line=f.readline()
    f.close()

    #del(status_info[0])
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