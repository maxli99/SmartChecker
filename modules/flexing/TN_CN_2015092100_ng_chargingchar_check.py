# -*- coding: utf-8 -*-
u"""Gx 接口使用后部分用户不产生话单（华为PCRF和CC=0用户问题）

添加下面的配置即可避免上述的问题。

charchar-index = 0
charging-profile = charging-profile-1

建议将其余字段均使用缺省的计费方式。
When enable gx function, subscriber with CC=0 's GX CCR message will set th online and 
offline as disable and the charging mode decide by PCRF . But Huawei PCRF will return 
disable , so these subsciber(CC=0) will not generate CDR.
You can add the followed config to resolve the problem:
charchar-index = 0
charging-profile = charging-profile-1
other cc=1,2,3,5,6,7,9 can use the same way.
"""
import re
from libs.checker import ResultInfo,CheckStatus
from libs.infocache import shareinfo
from libs.flexing import FlexiNG

__author__ = "richard.hu@nokia.com"

## Mandatory variables 
##--------------------------------------------
module_id = '20160304.01'
tag       = ['flexing','china']
priority  = 'critical'
name      = u"校验Session Profile中的Charging character配置"
desc      = __doc__
criteria  = u"""发生问题的前提条件：
1. 用户在 HLR/HSS 的 CC（ChargingCharacteristics）字段被设置为 0。不符合集团规范
《中国移动分组域实时计费接口规范 V1.1.0》要求，集团规范设置为 0X0400（4） 表示
在线计费，设置为 0X0800（8）表示离线计费。
2. 使用了华为的 PCRF.
3. SAE/GGSN没有设置charging-index为0的charging profile

注意：本报告仅显示第三项内容的检查结果。
"""
result = ResultInfo(name,priority=priority)
error = ''
##--------------------------------------------



##--------------------------------------------
## Optional variables
target_version = ['3.1_1.0','3.2','15']    

## first get the block of each 'show session-profile'
## from each block we will get the session-profile 's name and charging-index config 
pats_charchar = {'session-profile-block': re.compile(r"show ng session-profile (.*)\n([\w\d-]+ = [\S]+[\s]+)+"), 
                 'session-profile-name': re.compile(r"session-profile-name = ([\w\d-]+)"),
                 'charchar-index': re.compile(r"charchar-index = 0"),
}
#charchar_str = "charchar-index = 0:%(charchar0)s

check_commands = [
    ('@fsclish', '#below commands should be executed in fsclish shell'),
    ('show ng session-profile *','## show the configuration of all session profiles'),
]

def read_block(logfile,blkname):
    loglines = file(logfile).readlines()

    return ''.join(loglines)

    
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    logtxt = read_block(logfile,'NG_Charing_status')
    
    charging_index_status=[]
    status = CheckStatus.UNCHECKED
    
    # check the NG version first.   
    ng = shareinfo.get('ELEMENT')
    if not ng.version:  # not version info found.
        #status = CheckStatus.UNKNOWN
        charging_index_status.append(u"- NG version can't be determindated.")
    else:
        match = ng.match_version(major=target_version)
        
        if match['major']: 
            charging_index_status.append(u"- NG version: " + ng.version['major'] + u" 在受影响的版本列表中. \n")
        else:
            charging_index_status.append(u"- NG version: " + ng.version['major'] + u" 不在受影响版本列表中. \n")
    
    # Get every session-profile-block
    session_profile_block=[]
    pat=pats_charchar['session-profile-block']
    logtmp=logtxt
    r=pat.search(logtxt)
    if (r):
        status = CheckStatus.PASSED
        while r<>None:
            session_profile_block.append(r.group())
            logtmp=logtmp[r.end():]
            r=pat.search(logtmp)
    
    # From each block get session-profile-name and charging-index info
    for block in session_profile_block:
        block_logs = block.split('\n')
        line_count = len(block_logs)
        line = 0
        sp_name=''
        sp_chargingindex=''
        while (line < line_count):
            sp_file_name = pats_charchar['session-profile-name'].search(block_logs[line])
            if sp_file_name:
                curr_sp_name=sp_file_name.group(1)
                if (curr_sp_name <> sp_name and sp_name <> ''):
                    if (sp_chargingindex==''):
                        charging_index_status.append(u'Session Name: ' + sp_name + ' have no Index=0 configuration.\n')
                        status = CheckStatus.FAILED
                    else:
                        charging_index_status.append(u'Session Name: ' + sp_name + ' have Index=0 configuration.\n')
                sp_name=curr_sp_name
                sp_chargingindex = ''
                line = line + 1
                continue
            chargingindex = pats_charchar['charchar-index'].search(block_logs[line])
            if chargingindex:
                sp_chargingindex = 'FIND'
            line = line + 1
        if (sp_chargingindex==''):
            charging_index_status.append(u'Session Name: ' + sp_name + ' have no Index=0 configuration.\n')
            status = CheckStatus.FAILED
        else:
            charging_index_status.append(u'Session Name: ' + sp_name + ' have Index=0 configuration.\n')
        
    #pat=pats_charchar['session-profile-name']
    #for block in session_profile_block:
    #    r=pat.search(block)
    #    if r:
    #        session_profile_name=r.group(1)
    #        pat1=pats_charchar['charchar-index']
    #        r=pat1.search(block)
    #        if r:
    #            if status == CheckStatus.UNCHECKED:
    #                status = CheckStatus.PASSED
    #            charging_index_status.append(session_profile_name + ' have charchar-index=0 \n')
    #        else:
    #            if status == CheckStatus.UNCHECKED:
    #                status = CheckStatus.FAILED
    #            charging_index_status.append(session_profile_name + ' have NOT charchar-index=0 \n')
    #
    #if status == CheckStatus.UNCHECKED:
    #    status = CheckStatus.UNKNOWN
    #print charging_index_status 
    result.update(status=status,info=charging_index_status,error=error)
    return result
    
