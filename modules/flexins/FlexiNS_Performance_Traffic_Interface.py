# -*- coding: utf-8 -*-

u"""
 检查Flexi NS设备接口流量
    --通过网管数据库获取MME/SGSN的接口流量。
    --获取数据指令:
        OSS_query_v2.exe -D2016/07/25 -T1000 -d2016/07/25 -t1200 -cTCPIP_IPS_TOTAL,TCPIP_IPS_DELIVERED,TCPIP_TCPS_SNDTOTAL,TCPIP_TCPS_SNDPACK -uMME -l1
"""

import re
import json
from libs.checker import ResultInfo,CheckStatus
from libs.infocache import shareinfo
from libs.tools import MessageBuffer,debugmsg
from libs.flexins import FlexiNS

__author__ = 'liming.wang'
__email__  = 'liming.wang@nokia.com'
__date__   = '2016-07-29'

## Mandatory variables
##--------------------------------------------
module_id = 'FlexiNS_Performance_Traffic_Interface'
tag       = ['flexins','china']
priority  = 'major'
name      = u"NS 接口流量检查"
desc      = __doc__
criteria  = u"""
（1）检查接口流量
（2）如果接口流量超过100Mbps，则显示为Error，建议报现场工程师或客户关注。
"""
# traffic limit 100Mbps
LIMIT=100
result = ResultInfo(name,priority=priority)
error = ''
info = " %s %s, Check status: %s"

##--------------------------------------------
## Optional variables
target_version = ['N5', 'N6']

check_commands = [
    ('@ssh ossclient', "#below commands should be executed some site can conntect to OSS."),
    ('OSS_query_v2.exe -D2016/08/17 -T1200 -d2016/08/17 -t1300 -eSHMME06BNK -p60 -uUNIT_ID -cTCPIP_IPS_TOTAL,TCPIP_IPS_DELIVERED -l1'),
]


##--------------------------------------------
## Mandatory function: run
##--------------------------------------------

def run(logfile):
    result_info = []
    status_info = [CheckStatus.UNKNOWN]

    # init shareinfo


    logjson = json.load(open(logfile,'r'))

    col_desc = logjson['columndesc']
    rows = logjson['columns']
    ns = FlexiNS()
    ns._data['hostname'] = rows[0][0]
    shareinfo.set('ELEMENT',ns)

    if len(col_desc) > 0 and len(rows) > 0:
        status = CheckStatus.PASSED
        result_info.append('\t'.join(col_desc[0:5])+ '\tInTraffic'+'\tOutTraffic'+'\tCheckStatus')

        for row in rows:
            if row[5]=='UNKNOWN':
                continue
            interval=int(row[3])*60
            in_traffic=int(row[6])*8/interval/1024/1024
            out_traffic=int(row[7])*8/interval/1024/1024
            # CPPU and MMDU except from the statis (the data have problem)
            if in_traffic > LIMIT and out_traffic > LIMIT:
                status = CheckStatus.FAILED
            status_info.append(status)
            result_info.append('\t'.join(row[0:5]) + '\t' + str(in_traffic) + '\t' + str(out_traffic)
                               +'\t'+status)

    del(status_info[0])
    total_status=CheckStatus.FAILED
    if len(status_info)==0:
        error = "Can't find interface traffic info in this log!"
    elif status_info.count(CheckStatus.FAILED)>0:
        error="Check Failed!"
    else:
        error = ''
        total_status=CheckStatus.PASSED

    result.update(status=total_status, info=result_info, error=error)

    return result
