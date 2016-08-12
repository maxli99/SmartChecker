# -*- coding: utf-8 -*-
u"""
检查FlexiNG 各单元状态
  - 检查指令:
      nginfo -s
    
    该指令列出当前各单元当前运行状态。

"""

import re,sys
from libs.checker import ResultInfo
from libs.checker import CheckStatus
from libs.infocache import shareinfo
from libs.log_spliter import LogSpliter

__author__ = 'OuYangMingLi'
__email__  = 'mingli.l.ouyang@nokia.com'
__date__   = '20160807'

## Mandatory variables 
##--------------------------------------------
#module_id = 'NSTCN_20160718'
module_id = 'FlexiNG_Basic_System_UnitState'
tags      = ['china', 'flexing']
priority  = 'minor'
name      = u"FlexiNG 单元状态检查"
desc      = __doc__
criteria  = u"""
（1）检查NG版本为 ['3.1','3.2','15','16'] 或者更高版本。
（2）检查各单元状态，并输出状态列表。

"""
result = ResultInfo(name,module_id=module_id,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['3.1', '3.2', '15', '16']  

##在这里添加获取所需log的命令
check_commands = [
    #("ZWQO:CR;","show the NS packages information"),
    ("nginfo -s","show the NG Node and Cluster status"),
    #('ZDDE:{@UNIT_ID}:"cat /proc/cpuinfo | grep processor",;',"show CPU info of all CPU blade"),
]

### below add the optional functions for checking

#
# 在这里添加检查的辅助子程序
#
def Find_NG_Patt_Return_Info_List(LogFile,CommandStr,InfoPatt,ReturnInfoLen):
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
	return return_info_list

def createNgUnitStatusDic(return_info_list):
	return_ng_unit_info_dic = {}
	for UnitNameid in range(0,len(return_info_list),2):
		UnitName = return_info_list[UnitNameid]
		return_ng_unit_info_dic[UnitName] = return_info_list[UnitNameid+1]
	return return_ng_unit_info_dic

def FindNgUnitStatus(return_ng_unit_info_dic):
	return_ng_unit_ok_list = []
	return_ng_unit_nok_list = []
	ng_unit_list = return_ng_unit_info_dic.keys()
	ng_unit_list.sort()
	for ng_unit_name in ng_unit_list:
		if return_ng_unit_info_dic[ng_unit_name] == 'OK':
			return_ng_unit_ok_list.append(ng_unit_name)
		else:
			return_ng_unit_nok_list.append(ng_unit_name)
	return return_ng_unit_ok_list,return_ng_unit_nok_list

def printNgUnitStatusList(ng_unit_list,status_str):
	UnitMsg = ''
	for unitName in ng_unit_list:
		UnitMsg += '\n-  '+unitName+','+status_str
	return UnitMsg

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
        ngUnitPatt = r'/(\w{0,3}\d{0,2}?-\d+)\s+([N]?OK)\s+\w+\s*$'
        return_info_list = Find_NG_Patt_Return_Info_List(logfile,"nginfo\s+-s",ngUnitPatt,2)
        #print 'return_info_list = ',return_info_list
        return_ng_unit_info_dic = createNgUnitStatusDic(return_info_list)
        #print 'return_ng_unit_info_dic = ',return_ng_unit_info_dic
        ng_unit_ok_list,ng_unit_nok_list = FindNgUnitStatus(return_ng_unit_info_dic)
        okUnitMsg = printNgUnitStatusList(ng_unit_ok_list,"OK")
        nokUnitMsg = printNgUnitStatusList(ng_unit_nok_list,"NOK")
        if nokUnitMsg == '':
        	status=CheckStatus.PASSED
        else:
        	nokUnitMsg_1 = u"- 检查到NG部分单元状态异常"
        	errmsg = nokUnitMsg_1 + nokUnitMsg
        	status=CheckStatus.FAILED
        okUnitMsg_1 = u"- 检查到NG的版本为'%s',它属于%s或者更高版本" % (version_str,target_version)
        _msg = okUnitMsg_1 + okUnitMsg
        result.update(status=status,info=_msg,error=errmsg)
   
    ##网元版本不符合条件
    elif vstatus == CheckStatus.VERSION_UNMATCHED:
        result.update(status=CheckStatus.FAILED,info=[msg],error=errmsg)
    
    return result