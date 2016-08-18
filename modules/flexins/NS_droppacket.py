# -*- coding: utf-8 -*-

u"""
 检查Flexi NS设备丢包数量。
    --通过网管数据库获取MME/SGSN的丢包数量。
    --获取数据指令:
        OSS_query_v2.exe -D2016/07/25 -T1000 -d2016/07/25 -t1200 -cTCPIP_IPS_TOTAL,TCPIP_IPS_DELIVERED,TCPIP_TCPS_SNDTOTAL,TCPIP_TCPS_SNDPACK -uMME -l1
    --如果出现丢包较多的现象，请联系现场工程师修复。
"""

import re
import json
from libs.checker import ResultInfo,CheckStatus
from libs.infocache import shareinfo
from libs.tools import MessageBuffer,debugmsg
from libs.flexins import FlexiNS


## Mandatory variables 
##--------------------------------------------
module_id = 'NS_droppacketdata'
tag       = ['flexins','china']
priority  = 'major'
name      = u"NS 丢包数据检查"
desc      = __doc__
criteria  = u"""
（1）检查MME/SGSN版本为 ['N5 1.17-5','N5 1.19-3'] 或者更高版本。
（2）检查丢包数据。
（3）如果丢包数据15分钟多于1MB，则显示为Error，建议报现场工程师或客户检修。
"""
result = ResultInfo(name,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['N5 1.17-5','N5 1.19-3']   

check_commands = [
    ('@ssh ossclient', "#below commands should be executed some site can conntect to OSS."),
    ('OSS_query_v2.exe -D2016/08/17 -T1200 -d2016/08/17 -t1300 -eSHMME06BNK -p60 -uUNIT_ID -cTCPIP_IPS_TOTAL,TCPIP_IPS_DELIVERED -l1','## get ns data about the count of packets dropped'),
]

DROPPACKET_THRESHOLD = 0.01
blankstr = '                    '

def read_block(logfile,blkname):
    loglines = file(logfile).readlines()

    return ''.join(loglines)


def expandstr(data_rec,length):
    i = 0
    # print each column in record
    while (i < len(data_rec)):
        # some columns include only one item , some columns include items split by ','
        if ( data_rec[i].split(',') > 0 ):
            data_rec_temp = data_rec[i]
            data_rec[i] = ''
            for data in data_rec_temp.split(','):
                if (len(data) < length):
                    data_rec[i] = data_rec[i] + data + blankstr[:length-len(data)]    
        elif (len(data_rec[i]) < length):
            data_rec[i]=data_rec[i] + blankstr[:length-len(data_rec[i])]
        i = i + 1
    return data_rec
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

    check_info = []
    
    # init shareinfo
    ns = FlexiNS()
    ns._data['hostname'] = 'MME'
    shareinfo.set('ELEMENT',ns)
    
    logtxt = read_block(logfile,'OSS_DropPacket_Data')
    logjson = json.loads(logtxt)
    status = CheckStatus.UNCHECKED
    #print logjson
	# From the logdata get packet drop count ratio
    data_desc = logjson['columndesc']
    data_logs = logjson['columns']

    if (len(data_desc) > 0 and len(data_logs) > 0):
        status = CheckStatus.PASSED
        
        check_info.append('\t'.join(expandstr(data_desc,20)) + '\tDropPacketRatio')

        for data_log in data_logs:
            # Get the packets deliverd and total
            packet_deliver = float(data_log[5])
            packet_total = float(data_log[4])
            # CPPU and MMDU except from the statis (the data have problem)
            if (data_log[3][0:4]=='CPPU' or data_log[3][0:4]=='MMDU' ):
                continue
            if (packet_total > 0 and packet_total > packet_deliver): 
                packet_dropratio = 1 - packet_deliver/packet_total
                packet_dropratio = float('%0.3f'%packet_dropratio)
                if packet_dropratio > DROPPACKET_THRESHOLD:
                    status = CheckStatus.FAILED
            # make every sensor data item not less than 20 chars
            
                check_info.append('\t'.join(expandstr(data_log,20)) + '\t' + str(packet_dropratio*100) + '%')
            
	
	#print status
    #print check_info
    #print status
    if status == CheckStatus.UNCHECKED:
        status = CheckStatus.UNKNOWN

    result.update(status=status,info=check_info,error=error)
    return result