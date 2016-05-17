# -*- coding: utf-8 -*-

u"""
 检查Flexi NS设备的WDU磁盘碎片率
    --在MME/SGSN升级前,或发现MME/SGSN操作变得缓慢,建议检查硬盘的碎片率是否有较高的现象。
    --检查指令:
        ZDDE:OMU:"ZMA:W0,F3,,,,,","ZMA:W1,F3,,,,,","ZGSC:,00FC";
        ZDDE:MCHU:"ZMA:W0,F3,,,,,","ZMA:W1,F3,,,,,","ZGSC:,00FC";
        如果磁盘碎片率大于60%,判断为偏高。
    --检查指令可能会对硬盘有影响，执行后，请检查硬盘状态。
        ZISI:,:WDU,;
    --如果出现磁盘碎片率偏高的现象，请按照TN-Flexi_NS-SW0013-CI2中介绍修复。
"""

import re
from libs.checker import ResultInfo,CheckStatus
from libs.flexins import FlexiNS
from libs.flexins import get_ns_version
from libs.infocache import shareinfo


## Mandatory variables 
##--------------------------------------------
module_id = 'NSTNTS_SW0013'
tag       = ['flexins','china']
priority  = 'major'
name      = u"TN_TS_SW0013_CI2 FNS MME/SGSN 磁盘碎片率检查"
desc      = __doc__
criteria  = u"""
（1）检查MME/SGSN版本为 ['N5 1.19-3','N5 1.17-5'] 或者更高版本。
（2）检查OMU，MCHU的硬盘碎片率是否大于60%。大于为FAILED，小于则为PASSED。
（3）如果log中没有相应的指令log，结果为UNKNOWN。
"""
result = ResultInfo(name,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['N5 1.17-5','N5 1.19-3']    

pats_fragment = {'OMU-WDU0': re.compile(r"ZDDE:OMU.*?WDU-0.*?Fragmentation degree ",re.S),
        'OMU-WDU1': re.compile(r"ZDDE:OMU.*?WDU-1.*?Fragmentation degree ",re.S),
        'MCHU-WDU0': re.compile(r"ZDDE:MCHU.*?WDU-0.*?Fragmentation degree ",re.S),
        'MCHU-WDU1': re.compile(r"ZDDE:MCHU.*?WDU-1.*?Fragmentation degree ",re.S),
}
#fragmentstatus_str = "NS Version:%(nsversion)s, OMU(WDU-0):%(OMU-WDU0)s, OMU(WDU-1):%(OMU-WDU1)s, MCHU(WDU-0):%(MCHU-WDU0)s, MCHU(WDU-1):%(MCHU-WDU1)s"
##
fragmentstatus_str = "NS Version:%(nsversion)s OMU(WDU-0):%(OMU-WDU0)s OMU(WDU-1):%(OMU-WDU1)s MCHU(WDU-0):%(MCHU-WDU0)s MCHU(WDU-1):%(MCHU-WDU1)s"

check_commands = [
    ("ZWQO:CR;","show the NS packages information"),
    ("ZDDE:OMU:\"ZMA:W0,F3,,,,,\",\"ZMA:W1,F3,,,,,\",\"ZGSC:,00FC\";","show OMU WDU fragment ratio"),
    ("ZDDE:MCHU:\"ZMA:W0,F3,,,,,\",\"ZMA:W1,F3,,,,,\",\"ZGSC:,00FC\";","show MCHU WDU fragment ratio"),
]
def read_block(logfile,blkname):
    loglines = file(logfile).readlines()

    return ''.join(loglines)

 
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

    fragment_status={name:'' for name in pats_fragment}
    
    # Check NS Version

    ns = shareinfo.get('ELEMENT')
    if not ns.version:
        ns_status="No version info was found."
    else:
        nsversion = ns.version['BU']
        if ns.match_version(target_version):
            fragment_status['nsversion']=u"    - NS version: " + nsversion + u" 在支持版本清单里. \n"    
        else:
            fragment_status['nsversion']=u"    - NS version: " + nsversion + u" 不在支持版本清单里. \n"
    
    logtxt = read_block(logfile,'NS_fragment_status')
    
    
    status = CheckStatus.UNCHECKED
    
    for name,pat in pats_fragment.items():
        r=pat.search(logtxt)
        #print r.end()
        if r:
            logpos=r.end()
            if status == CheckStatus.UNCHECKED:
                status = CheckStatus.PASSED
            fragment_status[name] = logtxt[logpos:logpos+5]
            if fragment_status[name] > '60.0':
                status = CheckStatus.FAILED
            
    #print fragementstatus_str, fragment_status
    if status == CheckStatus.UNCHECKED:
        status = CheckStatus.UNKNOWN
    

    result.update(status=status,info=[fragmentstatus_str % fragment_status],error=error)
    return result
    