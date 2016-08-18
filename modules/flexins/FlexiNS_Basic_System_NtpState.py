# -*- coding: utf-8 -*-
u"""
检查FlexiNS NTP状态
  - 检查指令:
      ZDCP:;
    
    该指令列出当前的NTP服务运行状态。

"""

import re,sys,time
from libs.checker import ResultInfo
from libs.checker import CheckStatus
from libs.infocache import shareinfo
from libs.log_spliter import LogSpliter ,LOG_TYPE_FLEXI_NS

__author__ = 'OuYangMingLi'
__email__  = 'mingli.l.ouyang@nokia.com'
__date__   = '20160716'

## Mandatory variables 
##--------------------------------------------
#module_id = 'NSTCN_20160716'
module_id = 'FlexiNS_Basic_System_NtpState'
tags      = ['china', 'flexins']
priority  = 'minor'
name      = u"FlexiNS NTP状态检查"
desc      = __doc__
criteria  = u"""
（1）检查MME版本为 ['N5','N6'] 或者更高版本。
（2）检查NTP服务状态是否正常，是否与上级同步。

"""

result = ResultInfo(name,module_id=module_id,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['N5', 'N6']  

##在这里添加获取所需log的命令
check_commands = [
    ("ZWQO:CR;","show the NS packages information"),
    ('ZDCP:;',"show the state of NTP"),
]

### below add the optional functions for checking

#
# 在这里添加检查的辅助子程序
#
def read_block(logfile,blkname):
    logspliter=LogSpliter(type=LOG_TYPE_FLEXI_NS)
    logspliter.load(logfile)
    return logspliter.get_log(blkname,fuzzy=True)

#blocks = read_block(logfile,'ZDDE:SMMU,')

def FindNsNtpIp(logstr):
    result_tmp = []
    patternstr=r'\s*\d+\.\s+\*\s+(\d+.\d+.\d+.\d+)'
    try:
        unitresult=re.findall(patternstr,logstr,re.DOTALL)
        #print unitresult
    finally:
        if(len(unitresult)>0):
            result_tmp = unitresult
    return result_tmp

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    status = CheckStatus.UNCHECKED 
    errmsg = ''    
    
    ne = shareinfo.get('ELEMENT')
    # Check network element's Version
    vstatus,msg = ne.version_in_list(target_version)
    #print "vstatus = ",vstatus
    #print "msg = ",msg
    #print "result = ",result
    
    ##无法获得版本信息
    if vstatus == CheckStatus.VERSION_UNKNOWN:
        result.update(status=CheckStatus.UNKNOWN,info=[msg],error=error)
    
    ##网元版本符合条件
    elif vstatus== CheckStatus.VERSION_MATCHED:
        #
        # 在这里运行检查的内容
        #   
        blocks = read_block(logfile,'ZDCP')
        if len(blocks)>0:
            logstr = blocks[0]
            errmsg_log = ''
        else:
            logstr = ''
            errmsg_log = u'未检查到查询命令 "ZDCP:;" '
        logstr = str(logstr)
        #print type(logstr),"logstr = ",logstr
        NS_Ntp_Ip_List = FindNsNtpIp(logstr)
        #print 'NS_Ntp_Ip_List = ',NS_Ntp_Ip_List

        msg_unit_raw = u'- NTP服务上级服务器地址为：'
        msg_unit = ''
        if len(NS_Ntp_Ip_List) > 0:
        	status=CheckStatus.PASSED
       		msg_unit = msg_unit_raw + NS_Ntp_Ip_List[0] + '\n'
       		errorUnitMsg = ''
        else:
        	status=CheckStatus.FAILED
        	errorUnitMsg = u'未找到NTP上级同步IP地址，NTP服务异常，请登录网元进行确认'
        if errmsg_log == '':
        	errmsg = errmsg_log + errorUnitMsg
        else:
        	status=CheckStatus.UNKNOWN
        	errmsg = errmsg_log
        _msg = [msg,msg_unit]
        result.update(status=status,info=_msg,error=errmsg)
   
    ##网元版本不符合条件
    elif vstatus == CheckStatus.VERSION_UNMATCHED:
        result.update(status=CheckStatus.UNKNOWN,info=[msg],error=errmsg)
    
    return result