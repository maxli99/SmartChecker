# -*- coding: utf-8 -*-
u"""
检查FlexiNG NTP服务的状态
  - 检查指令:
      ntpq -p
    
    该指令列出当前NTP服务当前运行状态。

"""

import re,sys
from libs.checker import ResultInfo
from libs.checker import CheckStatus
from libs.infocache import shareinfo
from libs.log_spliter import LogSpliter

__author__ = 'OuYangMingLi'
__email__  = 'mingli.l.ouyang@nokia.com'
__date__   = '20160808'

## Mandatory variables 
##--------------------------------------------
#module_id = 'NSTCN_2016071802'
module_id = 'FlexiNG_Basic_System_NtpState'
tags      = ['china', 'flexing']
priority  = 'minor'
name      = u"FlexiNG NTP服务状态检查"
desc      = __doc__
criteria  = u"""
（1）检查NG版本为 ['3.1','3.2','15','16'] 或者更高版本。
（2）检查NTP服务状态，并输出NTP上级同步IP。

"""
result = ResultInfo(name,module_id=module_id,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['3.1', '3.2', '15', '16']  

##在这里添加获取所需log的命令
check_commands = [
    #("ZWQO:CR;","show the NS packages information"),
    ("ntpq -p","show the NTP status"),
]

### below add the optional functions for checking

#
# 在这里添加检查的辅助子程序
#
def Find_NG_Patt_Return_Info_List(LogFile,CommandStr,InfoPatt,ReturnInfoLen):
	Command_start_find_id = 0 # 0 means not find,1 means have find
	Command_start=False
	Command_end=False
	return_info_list=[]
	cur_str = '[$#]'
	Command_start_Patt=r"%s\s*%s\s*" % (cur_str,CommandStr)
##	print "Command_start_Patt =",Command_start_Patt
	Command_end_Patt=r"%s\s*" % (cur_str)
	Find_Info_Patt=InfoPatt
	#print "Find_Info_Patt =",Find_Info_Patt
	return_Len = ReturnInfoLen+1
	fp=open(LogFile,'r')
	for line in fp.readlines():
		if Command_start==False and Command_end==False:
			m=re.search(Command_start_Patt,line)
			if m:
				Command_start=True
				Command_start_find_id = 1
				#print line
				continue
		elif Command_start==True and Command_end==False:
			m0=re.search(Command_end_Patt,line)
			m1=re.search(Find_Info_Patt,line)
			if m0:
				Command_end=True
				#print line
				continue
			if m1:
				#print "line =",line
				for infoId in range(1,return_Len):
					try:
						return_info_list.append(m1.group(infoId))
					except IndexError:
						return_info_list.append('Not_Find_Infomation')
				continue
		else:
			break
	fp.close()
	return return_info_list,Command_start_find_id

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    status = CheckStatus.UNCHECKED
    errmsg = []
    
    ne = shareinfo.get('ELEMENT')
    #print type(shareinfo.get('ELEMENT'))
    # Check network element's Version
    #print 'ne = ',ne
    hostname = ne.hostname
    try:
        version_str = ne.version['major']
#        vstatus= CheckStatus.VERSION_MATCHED
    except KeyError:
        version_str = None
        vstatus = CheckStatus.VERSION_UNKNOWN
        msg = u'未找到NG版本信息，请确认是否有查询版本信息LOG'
    if version_str in target_version:
        vstatus = CheckStatus.VERSION_MATCHED
    else:
        vstatus = CheckStatus.VERSION_UNMATCHED
        msg = u"- 检查到NG的版本为'%s',它不属于%s或者更高版本" % (version_str,target_version)

    #print "vstatus = ",vstatus
    ##无法获得版本信息
    if vstatus == CheckStatus.VERSION_UNKNOWN:
        result.update(status=CheckStatus.UNKNOWN,info=[msg],error=error)
    
    ##网元版本符合条件
    elif vstatus== CheckStatus.VERSION_MATCHED:
        #
        # 在这里运行检查的内容
        #   
        _msg = ''

        ngNtpPatt = r'\*(\d+.\d+.\d+.\d+)\s+\d+.\d+.\d+.\d+\s+\d+\s+\w+\s+\S+\s+\S+\s+(\S+)\s+\S+\s+(\S+)\s*'
        return_info_list,serchCommandId = Find_NG_Patt_Return_Info_List(logfile,"ntpq\s*-p",ngNtpPatt,3)
        #print 'return_info_list = ',return_info_list
        msg_ntp_raw0 = u"- 检查到NG的版本为'%s',它属于%s或者更高版本" % (version_str,target_version)
        msg_ntp_raw = msg_ntp_raw0 + '\n' + u'- NTP服务上级同步服务器地址为：'
        if len(return_info_list)>0:
        	reach_v = int(return_info_list[1])
        	offset_v = float(return_info_list[2])
        	msg_unit = msg_ntp_raw + return_info_list[0] + '\n'
        	if reach_v > 0 and abs(offset_v) < 1000:
        		status=CheckStatus.PASSED
        		errorUnitMsg = ''
        	else:
        		status=CheckStatus.FAILED
        		errorUnitMsg = u'NTP与上级同步时间异常，请登录网元进行确认'
        else:
        	status = CheckStatus.UNCHECKED
        	msg_unit = msg_ntp_raw + 'None' + '\n'
        	if serchCommandId:
        		errorUnitMsg = u'未找到查询NTP状态信息，请确认NTP服务是否开启'
        	else:	
        		errorUnitMsg = u'未找到NTP状态查询命令 ntpq -p ，请确认是否有进行查询'
        errmsg = errorUnitMsg
        _msg = msg_unit
        
        result.update(status=status,info=_msg,error=errmsg)
   
    ##网元版本不符合条件
    elif vstatus == CheckStatus.VERSION_UNMATCHED:
        result.update(status=CheckStatus.FAILED,info=[msg],error=errmsg)
    
    return result