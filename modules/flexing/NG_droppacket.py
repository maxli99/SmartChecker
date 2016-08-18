# -*- coding: utf-8 -*-

u"""
 检查Flexi NG设备丢包数量。
    --通过网管数据库获取SAEGW/GGSN的丢包数量。
    --获取数据指令:
        OSS_query_v2.exe -D2016/07/25 -T1000 -d2016/07/25 -t1200 -cQOS_DL_DROP_QCI -uSAEGW -l1
    --如果出现丢包较多的现象，请联系现场工程师修复。
"""

import re
import json
from libs.checker import ResultInfo,CheckStatus
from libs.infocache import shareinfo
from libs.tools import MessageBuffer,debugmsg
from libs.flexing import FlexiNG


## Mandatory variables 
##--------------------------------------------
module_id = 'NG_droppacketdata'
tag       = ['flexing','china']
priority  = 'major'
name      = u"NG 丢包数据检查"
desc      = __doc__
criteria  = u"""
（1）检查SAEGW/GGSN版本为 ['NG 3.15','NG 3.16'] 或者更高版本。
（2）检查丢包数据。
（3）如果丢包数据15分钟多于1MB，则显示为Error，建议报现场工程师或客户检修。
"""
result = ResultInfo(name,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['3.1','3.2','15','16']    

check_commands = [
    ('@ssh ossclient', "#below commands should be executed some site can conntect to OSS."),
    ('OSS_query_v2.exe -D2016/07/25 -T1000 -d2016/07/25 -t1200 -cQOS_DL_DROP_QCI -uSAEGW -l1','## get ng data about the count of packets dropped'),
]

DROPPACKET_THRESHOLD = 1000000
blankstr = '                    '

def read_block(logfile,blkname):
    loglines = file(logfile).readlines()

    return ''.join(loglines)


def expandstr(data_rec,length):
    i = 0
    while (i < len(data_rec)):
        if (len(data_rec[i]) < length):
            data_rec[i]=data_rec[i] + blankstr[:length-len(data_rec[i])]
        i = i + 1
    return data_rec
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

    check_info = []
    
    # init shareinfo
    ng = FlexiNG()
    ng._data['hostname'] = 'SAEGW'
    shareinfo.set('ELEMENT',ng)
    
    logtxt = read_block(logfile,'OSS_DropPacket_Data')
    logjson = json.loads(logtxt)
    status = CheckStatus.UNCHECKED
    #print logjson
	# From the logdata get packet drop count
    data_desc = logjson['columndesc']
    data_logs = logjson['columns']

    if (len(data_desc) > 0 and len(data_logs) > 0):
        status = CheckStatus.PASSED
        
        check_info.append('\t'.join(expandstr(data_desc,20)))

        for data_log in data_logs:
            # check the temperature with TEMPERATURE_THRESHOLD
            if float(data_log[4]) > DROPPACKET_THRESHOLD:
                status = CheckStatus.FAILED
            # make every sensor data item not less than 20 chars
            
            check_info.append('\t'.join(expandstr(data_log,20)))
            
	
	#print status
    #print check_info
    #print status
    if status == CheckStatus.UNCHECKED:
        status = CheckStatus.UNKNOWN

    result.update(status=status,info=check_info,error=error)
    return result