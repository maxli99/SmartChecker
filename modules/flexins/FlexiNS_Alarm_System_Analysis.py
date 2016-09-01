# -*- coding: utf-8 -*-

u"""
 检查Flexi NS设备丢包数量。
    --通过网管数据库获取MME/SGSN的告警分析。
    --获取数据指令:
        OSS_query_v2.exe -D2016/07/25 -T1000 -d2016/07/25 -t1200 -cALARM -uMME -l1
    --如果出现某些告警较多的现象，请联系现场工程师修复。
"""

import re
import json
from libs.checker import ResultInfo,CheckStatus
from libs.infocache import shareinfo
from libs.tools import MessageBuffer,debugmsg
from libs.flexins import FlexiNS


## Mandatory variables 
##--------------------------------------------
module_id = 'NS_AlarmAnalysis'
tag       = ['flexins','china']
priority  = 'major'
name      = u"NS 告警信息检查"
desc      = __doc__
criteria  = u"""
（1）检查MME/SGSN版本为 ['N5 1.17-5','N5 1.19-3'] 或者更高版本。
（2）检查告警信息。
（3）如果出现critical告警，则显示为Error，建议报现场工程师或客户检修。
"""
result = ResultInfo(name,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['N5 1.17-5','N5 1.19-3']    


check_commands = [
    ('@ssh ossclient', "#below commands should be executed some site can conntect to OSS."),
    ('OSS_query_v2.exe -D2016/07/25 -T1000 -d2016/07/25 -t1200 -cALARM -uMME -l1','## get ng data about the count of packets dropped'),
]

CRITICAL_ALARM_COUNT = 1
blankstr = '                    '
AlarmTopCount = 5
AlarmSeverityThr = '1'

def read_block(logfile,blkname):
    loglines = file(logfile).readlines()

    return ''.join(loglines)

# for display the data with fixed width, need expand the column string
def expandstr(data_rec,length):
    i = 0
    while (i < len(data_rec)):
        if (len(data_rec[i]) < length):
            data_rec[i]=data_rec[i] + blankstr[:length-len(data_rec[i])]
        i = i + 1
    return data_rec

# Count the alarm by alarm number 
def getAlarmCount(data_logs,check_info):
    data_logs.sort(key=lambda l:(l[0],l[2]))
    data_buf = {}
    data_key = []
    for data_log in data_logs:
        data_key.append(data_log[0])  # NE_NAME
        data_key.append(data_log[2])  # Alarm Number
        data_key.append(data_log[7])  # Alarm Severity
        data_key.append(data_log[8])  # Alarm Text
        data_keystr  = '\t'.join(data_key)
        if data_key in data_buf.keys():
            data_buf[data_keystr] = data_buf[data_keystr] + 1
        else:
            data_buf[data_keystr] = 1
        data_key = []

    alarm_desc_title = [u'网元名称',u'告警号',u'告警级别',u'告警描述',u'数量']
    check_info.append('\t'.join(alarm_desc_title))
    for data_buf_key in sorted(data_buf.keys()):
        # make every sensor data item not less than 20 chars
        check_info.append(data_buf_key + '\t' + str(data_buf[data_buf_key]))
        
# Top 5 alarms according the severity
def getTopAlarmbySeverity(data_logs,check_info):
    
    status = CheckStatus.PASSED
    check_info.append('\n' + u'按告警级别排序')
    alarm_desc_title = [u'网元名称',u'对象名',u'告警号',u'告警时间',u'告警清除时间',u'告警状态',u'告警类型',u'告警级别',u'告警描述',u'告警补充信息']
    check_info.append('\t'.join(alarm_desc_title))
    data_logs.sort(key=lambda l:(l[7]))
    
    i = 0
    for data_log in data_logs:
        if (i < AlarmTopCount):
            if (str(data_log[7]) == AlarmSeverityThr):
                status = CheckStatus.FAILED
            check_info.append('\t'.join(data_log))
            i = i + 1
        else:
            break
        
    return status
    

# Top 5 alarms according the Alarm Time 
def getTopAlarmbyTime(data_logs,check_info):
    check_info.append('\n' + u'按告警时间倒序排序')
    alarm_desc_title = [u'网元名称',u'对象名',u'告警号',u'告警时间',u'告警清除时间',u'告警状态',u'告警类型',u'告警级别',u'告警描述',u'告警补充信息']
    check_info.append('\t'.join(alarm_desc_title))
    data_logs.sort(key=lambda l:(l[3]),reverse = True)
    
    i = 0
    for data_log in data_logs:
        if (i < AlarmTopCount):
            check_info.append('\t'.join(data_log))
            i = i + 1
        else:
            break
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

    check_info = []
    
    # init shareinfo
    ns = FlexiNS()
    ns._data['hostname'] = 'MME'
    shareinfo.set('ELEMENT',ns)
    
    logtxt = read_block(logfile,'OSS_Alarm_Info')
    logjson = json.loads(logtxt)
    status = CheckStatus.UNCHECKED
    #print logjson
	# From the logdata get packet drop count
    data_desc = logjson['columndesc']
    data_logs = logjson['columns']

    if (len(data_desc) > 0 and len(data_logs) > 0):
        status = CheckStatus.PASSED
        getAlarmCount(data_logs,check_info)
        status = getTopAlarmbySeverity(data_logs,check_info)
        getTopAlarmbyTime(data_logs,check_info)
	
	#print status
    #print check_info
    #print status
    if status == CheckStatus.UNCHECKED:
        status = CheckStatus.UNKNOWN

    result.update(status=status,info=check_info,error=error)
    return result