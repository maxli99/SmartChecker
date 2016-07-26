# -*- coding: utf-8 -*-

u"""
 检查Flexi NS设备各板卡的sensor数据，目前主要是温度。
    --在MME/SGSN,检查板卡的sensor数据是否有温度较高的现象。
    --检查指令:
        ZDDS;
        Z2CT:0:10.200.200.10/12/14
        clia sensordata
    --如果出现温度偏高的现象，请联系现场工程师修复。
"""

import re
from libs.checker import ResultInfo,CheckStatus
from libs.flexins import FlexiNS
from libs.flexins import get_ns_version
from libs.infocache import shareinfo

import textfsm


## Mandatory variables 
##--------------------------------------------
module_id = 'NS_Sensordata'
tag       = ['flexins','china']
priority  = 'major'
name      = u"NS 板卡Sensor数据温度检查"
desc      = __doc__
criteria  = u"""
（1）检查MME/SGSN版本为 ['N5 1.19-3','N5 1.17-5'] 或者更高版本。
（2）检查各板卡的Sensor数据，温度按大小排出Top 10。
（3）如果Sensor数据中出现温度有超过70摄氏度，则显示为Error，建议报现场工程师或客户检修。
"""
result = ResultInfo(name,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['N5 1.17-5','N5 1.19-3']    
sensor_scripts = {
	'SENSOR_TEMPERATURE             ':'modules\\flexins\\fsm_module\\ns_sensor_Temperature.fsm'
}

check_commands = [
    ('Z2CT:0:10.200.200.10/12/14', "#below commands should be executed in Shelfmanager."),
    ('clia sensordata','## show sensor data'),
]

sensor_temperate_titles = [
    u'MME/SGSN 框        ',
    u'槽位 （板卡类型）   ',
    u'Sensor 名称        ',
    u'Sensor 数据类型    ',
    u'Sensor 数据值      '
]

sensor_frame = {
    '10.200.200.10':u'第一框             ',
    '10.200.200.12':u'第二框             ',
    '10.200.200.14':u'第三框             '
}

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

TEMPERATURE_THRESHOLD = 70

def read_block(logfile,blkname):
    loglines = file(logfile).readlines()

    return ''.join(loglines)

 
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

    blankstr = '                    '
    check_info = []
    # Check NS Version
    ns_version_status=""
    ns = shareinfo.get('ELEMENT')
    if not ns.version:
        ns_status="No version info was found."
    else:
        nsversion = ns.version['BU']
        if ns.match_version(target_version):
            ns_version_status=u"    - NS version: " + nsversion + u" 在支持版本清单里. \n"    
        else:
            ns_version_status=u"    - NS version: " + nsversion + u" 不在支持版本清单里. \n"
    
    check_info.append(ns_version_status)

    logtxt = read_block(logfile,'NS_Sensor_Temperature_status')
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
            fsminfos.sort(key=lambda x:x[4],reverse = True)
            showdatas=10
            for fsminfo in fsminfos:
                showdatas = showdatas - 1 
                fsminfo[0] = sensor_frame[fsminfo[0]]
                fsminfo[1] = slot_ipmb_adress[fsminfo[1]]
                
                # check the temperature with TEMPERATURE_THRESHOLD
                if float(fsminfo[4]) > TEMPERATURE_THRESHOLD:
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