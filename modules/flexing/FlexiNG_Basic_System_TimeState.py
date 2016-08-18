# -*- coding: utf-8 -*-
u"""
检查FlexiNG CLA和各AS板卡时间是否一致
  - 检查指令:
      date +%s
      ssh AS{X}-{X} "date +%s"
    
    该指令列出主用CLA和各AS板卡的当前运行时间。

"""

import re,sys,time
from libs.checker import ResultInfo
from libs.checker import CheckStatus
from libs.infocache import shareinfo
from libs.log_spliter import LogSpliter

__author__ = 'OuYangMingLi'
__email__  = 'mingli.l.ouyang@nokia.com'
__date__   = '20160808'

## Mandatory variables 
##--------------------------------------------
#module_id = 'NSTCN_2016071803'
module_id = 'FlexiNG_Basic_System_TimeState'
tags      = ['china', 'flexing']
priority  = 'minor'
name      = u"FlexiNG 板卡时间检查"
desc      = __doc__
criteria  = u"""
（1）检查NG版本为 ['3.1','3.2','15','16'] 或者更高版本。
（2）检查CLA和各AS板卡时间是否一致，并输出其查询时的时间。

"""
result = ResultInfo(name,module_id=module_id,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['3.1', '3.2', '15', '16']  

##在这里添加获取所需log的命令
check_commands = [
    ("date +%s","show the Master CLA Time"),
    ('ssh AS{X}-{X} "date +%s"',"show the AS Blade Time"),
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
	#print "Command_start_Patt =",Command_start_Patt
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

def FindNgAsTimeInfo(logFileName):
    result_tmp = {}
    fpstr=file(logFileName).readlines()
    logstr = "".join(fpstr)
    patternstr=r'ssh\s*(AS\d+-\d+)\s+"date\s*\+\%s"\s*\r*\n*\s*(\d+)\s*'
    try:
        unitresult=re.findall(patternstr,logstr,re.DOTALL)
        #print unitresult
    finally:
        if(len(unitresult)>0):
            for AsNodeName,AsTime in unitresult:
                result_tmp[AsNodeName]=AsTime
    return result_tmp

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
        msg = u'- 未找到NG版本信息，请确认是否有查询版本信息LOG'
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
        ng_time_info_dic = {}
        ngTimePatt = r'^\s*(\d+)\s*$'
        ngAsTimePatt = r'^\s*(\d+)\s*$'
        return_info_list,serchCommandId = Find_NG_Patt_Return_Info_List(logfile,"date\s*\+\%s\s*$",ngTimePatt,1)
        #print 'return_info_list = ',return_info_list
        if len(return_info_list)>0:
        	ng_time_info_dic['CLA'] = return_info_list[0]
        as_time_info_dic = FindNgAsTimeInfo(logfile)
        ng_time_info_dic.update(as_time_info_dic)
        #print 'ng_time_info_dic = ',ng_time_info_dic
        #print 'as_time_info_dic = ',as_time_info_dic
        msg_ntp_raw0 = u"- 检查到NG的版本为'%s',它属于%s或者更高版本" % (version_str,target_version)
        msg_ntp_raw = msg_ntp_raw0 + '\n'
        if len(ng_time_info_dic)>1:
        	ng_node_name_list = ng_time_info_dic.keys()
        	ng_node_name_list.sort()
        	ng_node_time_list = ng_time_info_dic.values()
        	ng_node_time_diff = int(max(ng_node_time_list))-int(min(ng_node_time_list))
        	msg_unit = ''
        	for ng_node_name in ng_node_name_list:
        		msg_unit_n = u'- %s板卡时间为：' % (ng_node_name)
        		msg_unit_t = ng_time_info_dic[ng_node_name]
        		msg_unit_t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(msg_unit_t)))
        		msg_unit = msg_unit + msg_unit_n + msg_unit_t + '\n'
        	msg_unit = msg_ntp_raw + msg_unit
        	if ng_node_time_diff < 600 and serchCommandId > 0:
        		status=CheckStatus.PASSED
        		errorUnitMsg = ''
        	else:
        		status=CheckStatus.FAILED
        		if serchCommandId == 0:
        			errorUnitMsg = u'未检查到主用CLA板卡时间信息，请确认是否有进行查询，查询命令为： date +%s'
        		else:
        			errorUnitMsg = u'检查到部分单元时间相差很大，请登录网元进行确认'
        elif len(ng_time_info_dic) == 1:
        	status = CheckStatus.UNCHECKED
        	ng_node_name_list = ng_time_info_dic.keys()
        	ng_node_name_list.sort()
        	msg_unit = ''
        	for ng_node_name in ng_node_name_list:
        		msg_unit_n = u'- %s板卡时间为：' % (ng_node_name)
        		msg_unit_t = ng_time_info_dic[ng_node_name]
        		msg_unit_t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(msg_unit_t)))
        		msg_unit = msg_unit + msg_unit_n + msg_unit_t + '\n'
        	msg_unit = msg_ntp_raw + msg_unit
        	if serchCommandId:
        		errorUnitMsg = u'未找到AS板卡当前时间信息，请确认是否有进行查询，具体查询哪些AS请根据网元配置情况决定，查询命令为：ssh AS3-0 "date +%s" '
        	else:	
        		errorUnitMsg = u'未检查到主用CLA板卡时间信息，请确认是否有进行查询，查询命令为： date +%s '
        else:
        	status = CheckStatus.UNCHECKED
        	msg_unit = msg_ntp_raw + u'- 未检查到主用CLA板卡和AS板卡时间信息' + '\n'
        	errorUnitMsg = u'未检查到主用CLA板卡时间信息，请确认是否有进行查询，查询命令为： date +%s ' + '\n' + u'未找到AS板卡当前时间信息，请确认是否有进行查询，具体查询哪些AS请根据网元配置情况决定，查询命令为：ssh AS3-0 "date +%s" '
        errmsg = errorUnitMsg
        _msg = msg_unit
        
        result.update(status=status,info=_msg,error=errmsg)
   
    ##网元版本不符合条件
    elif vstatus == CheckStatus.VERSION_UNMATCHED:
        result.update(status=CheckStatus.FAILED,info=[msg],error=errmsg)
    
    return result