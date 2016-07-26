# -*- coding: utf-8 -*-

u"""
 检查Flexi NG设备各板卡的sensor数据，目前主要是温度。
    --在SAEGW/GGSN,检查板卡的sensor数据是否有温度较高的现象。
    --检查指令:
        ssh SM-1 clia sensordata
    --如果出现温度偏高的现象，请联系现场工程师修复。
"""

import re
from libs.checker import ResultInfo,CheckStatus
from libs.infocache import shareinfo
from libs.tools import MessageBuffer,debugmsg

import textfsm


## Mandatory variables 
##--------------------------------------------
module_id = 'NG_Sensordata'
tag       = ['flexing','china']
priority  = 'major'
name      = u"NG 板卡Sensor数据温度检查"
desc      = __doc__
criteria  = u"""
（1）检查SAEGW/GGSN版本为 ['NG 3.15','NG 3.16'] 或者更高版本。
（2）检查各板卡的Sensor数据，温度按大小排出Top 10。
（3）如果Sensor数据中出现温度有超过75摄氏度，则显示为Error，建议报现场工程师或客户检修。
"""
result = ResultInfo(name,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['3.1','3.2','15','16']    
sensor_scripts = {
	'SENSOR_TEMPERATURE             ':'modules\\flexing\\fsm_module\\sensor_Temperature.fsm'
}

check_commands = [
    ('@ssh sm-1', "#below commands should be executed in SM-1."),
    ('clia sensordata','## show sensor data'),
]

sensor_temperate_titles = [
    u'槽位 （板卡类型）   ',
    u'Sensor 名称        ',
    u'Sensor 数据类型    ',
    u'Sensor 数据值      '
]
slot_ipmb_adress = {
    '9e':'1       (node blade)',
    '9a':'2       (node blade)',
    '96':'3       (node blade)',
    '92':'4       (node blade)',
    '8e':'5       (node blade)',
    '8a':'6       (node blade)',
    '86':'7       (node blade)',
    '82':'8       (hub blade) ',
    '84':'9       (hub blade) ',
    '88':'10      (node blade)',
    '8c':'11      (node blade)',
    '90':'12      (node blade)',
    '94':'13      (node blade)',
    '98':'14      (node blade)',
    '9c':'15      (node blade)',
    'a0':'16      (node blade)',
    '10':'left shelfmanager   ',
    '12':'left shelfmanager   ',
    '20':'active shelfmanager '
}

TEMPERATURE_THRESHOLD = 75

def read_block(logfile,blkname):
    loglines = file(logfile).readlines()

    return ''.join(loglines)

 
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

    blankstr = '                    '
    # Check NG Version
    check_info = []
    
    ng = shareinfo.get('ELEMENT')
    if not ng.version:  # not version info found.
        #status = CheckStatus.UNKNOWN
        check_info.append(u"- NG version can't be determindated.")
    else:
        match = ng.match_version(major=target_version)
        
        if match['major']: 
            check_info.append(u"- NG version: " + ng.version['major'] + u" 在受影响的版本列表中. \n")
        else:
            check_info.append(u"- NG version: " + ng.version['major'] + u" 不在受影响版本列表中. \n")

    logtxt = read_block(logfile,'NG_Sensor_Temperature_status')
    status = CheckStatus.UNCHECKED
    
	# From the logfile get Sensor Temperature
    for name,script in sensor_scripts.items():
        check_info.append(name)
        fsm = textfsm.TextFSM(open(script))
        fsminfos=fsm.ParseText(logtxt)
        #print len(fsminfos)
        if (len(fsminfos)>0):
            status = CheckStatus.PASSED
            check_info.append('\t'.join(sensor_temperate_titles))
            fsminfos.sort(key=lambda x:x[3],reverse = True)
            showdatas=10
            for fsminfo in fsminfos:
                showdatas = showdatas - 1 
                fsminfo[0] = slot_ipmb_adress[fsminfo[0]]
                # check the temperature with TEMPERATURE_THRESHOLD
                if float(fsminfo[3]) > TEMPERATURE_THRESHOLD:
                    status = CheckStatus.FAILED
                # make every sensor data item not less than 20 chars
                i = 0
                while (i < len(fsminfo)):
                    if (len(fsminfo[i]) < 20):
                        fsminfo[i]=fsminfo[i] + blankstr[:20-len(fsminfo[i])]
                    i = i + 1
                
                check_info.append('\t'.join(fsminfo[0:]))
                if showdatas == 0 :
                    break
                check_info.append('\n')
			
	
	#print status
    #print check_info
    print status
    if status == CheckStatus.UNCHECKED:
        status = CheckStatus.UNKNOWN

    result.update(status=status,info=check_info,error=error)
    return result