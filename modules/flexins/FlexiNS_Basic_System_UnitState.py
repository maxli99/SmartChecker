# -*- coding: utf-8 -*-
u"""
检查FlexiNS 各个CPU 单元状态
  - 检查指令:
      ZUSI:COMP;
    
    该指令列出当前的CPU 单元状态情况。

"""

import re,sys,time
from libs.checker import ResultInfo
from libs.checker import CheckStatus
from libs.infocache import shareinfo
from libs.log_spliter import LogSpliter ,LOG_TYPE_FLEXI_NS

__author__ = 'OuYangMingLi'
__email__  = 'mingli.l.ouyang@nokia.com'
__date__   = '20160715'

## Mandatory variables 
##--------------------------------------------
#module_id = 'NSTCN_20160715'
module_id = 'FlexiNS_Basic_System_UnitState'
tags      = ['china', 'flexins']
priority  = 'minor'
name      = u"FlexiNS CPU 单元状态检查"
desc      = __doc__
criteria  = u"""
（1）检查MME版本为 ['N5','N6'] 或者更高版本。
（2）检查OMU/IPDU/MMDU/CPPU等单元状态为WO-EX或者SP-EX。

"""
#global_result_dic = {}
#global_result_dic['ns_unit_state'] = {}
result = ResultInfo(name,module_id=module_id,priority=priority)
error = ''


##--------------------------------------------
## Optional variables
target_version = ['N5', 'N6']  

##在这里添加获取所需log的命令
check_commands = [
    ("ZWQO:CR;","show the NS packages information"),
    ('ZUSI:COMP;',"show the state of CPU blade"),
]

### below add the optional functions for checking

#
# 在这里添加检查的辅助子程序
#
def read_block(logfile,blkname):
    logspliter=LogSpliter(type=LOG_TYPE_FLEXI_NS)
    logspliter.load(logfile)
    return logspliter.get_log(blkname,fuzzy=True)

def FindNsUnitWorkStatus(logstr):
    result_tmp = {}
    patternstr="\s+(\w{3,4})-(\d{1,2})\s+\w{4}\s(\w{2}-\w{2})\s+"
    try:
        unitresult=re.findall(patternstr,logstr,re.DOTALL)
        #print unitresult
    finally:
        if(len(unitresult)>0):
            for unitname,unitid,status in unitresult:
                 key=unitname+unitid 
                 result_tmp[key]=status
    return result_tmp

def checkUnitStateIsOk(UnitStateDic):
	UnitNameList = UnitStateDic.keys()
	UnitNameList.sort()
	UnitOkState = ['WO-EX','SP-EX']
	errorUnitDic = {}
	for unitName in  UnitNameList:
		unitStates = UnitStateDic[unitName]
		if unitStates in UnitOkState:
			pass
			#print unitName,unitStates,'  is OK !'
		else:
			#print unitName,unitStates,'  is Not OK !'
			errorUnitDic[unitName] = unitStates
	return errorUnitDic

def printNotOkUnitState(errorUnitDic):
	UnitNameList = errorUnitDic.keys()
	UnitNameList.sort()
	errorUnitMsg = ''
	for unitName in  UnitNameList:
		unitStates = errorUnitDic[unitName]
		errorUnitMsg += '\n-  '+unitName+','+unitStates
	#print errorUnitMsg
	return errorUnitMsg

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
    status = CheckStatus.UNCHECKED 
    errmsg = []    
    
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
        blocks = read_block(logfile,'ZUSI:COMP')
        if len(blocks)>0:
            logstr = blocks[0]
            errmsg_log = ''
        else:
            logstr = ''
            errmsg_log = u'未检查到查询命令 "ZUSI:COMP;" '
        logstr = str(logstr)
        #print type(logstr),"logstr = ",logstr
        NS_Unit_State_Dic = FindNsUnitWorkStatus(logstr)
        #print 'NS_Unit_State_Dic = ',NS_Unit_State_Dic
        Unit_Name = NS_Unit_State_Dic.keys()
        #print 'Unit_Name = ',Unit_Name
        Unit_Name.sort()
        msg_unit_raw = '-  '
        msg_unit = ''
        for Unit_str in Unit_Name:
        	msg_unit = msg_unit + msg_unit_raw + Unit_str + ' , ' + NS_Unit_State_Dic[Unit_str] + '\n'
        _msg = [msg,msg_unit]
        errorUnitDic = checkUnitStateIsOk(NS_Unit_State_Dic)
        if len(errorUnitDic) == 0:
        	status=CheckStatus.PASSED
        else:
        	status=CheckStatus.FAILED
        	errorUnitMsg = u'以下单元状态异常，请登录网元进行确认'
        	errmsgStr = printNotOkUnitState(errorUnitDic)
        	errmsg = errorUnitMsg + errmsgStr
        if errmsg_log != '':
        	status=CheckStatus.UNKNOWN
        	errmsg = errmsg_log
        result.update(status=status,info=_msg,error=errmsg)
   
    ##网元版本不符合条件
    elif vstatus == CheckStatus.VERSION_UNMATCHED:
        result.update(status=CheckStatus.UNKNOWN,info=[msg],error=errmsg)
    
    return result