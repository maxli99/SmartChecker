# -*- coding: utf-8 -*-

u"""
 输出MME/SGSN的关键参数
"""

import re
from libs.checker import ResultInfo,CheckStatus
from libs.flexins import FlexiNS
from libs.flexins import get_ns_version
from libs.infocache import shareinfo

import textfsm

## Mandatory variables 
##--------------------------------------------
module_id = 'NS_PARAMETER_CHECK'
tag       = ['flexins','china']
priority  = 'major'
name      = u"NS LTE KPI"
desc      = __doc__
criteria  = u"""
（1）检查MME/SGSN版本为 ['N5 1.19-3','N5 1.17-5'] 或者更高版本。
（2）整理输出log中的参数。
"""
result = ResultInfo(name,priority=priority)
error = ''

#
#def ratio_with_succ_fail(succstr,failstr):
#	if(succstr.isdigit()):
#		succnum=int(succ)
#	else:
#		succnum=0
#	if(failstr.isdigit()):
#		failnum=int(fail)
#	else:
#		failnum=0
#	if((succnum+failnum)<>0):
#		return succ/(succ+fail)
#	else:
#		return 0
##--------------------------------------------
## Optional variables
target_version = ['N5 1.17-5','N5 1.19-3']    

parameter_scripts = {
	'LTE Paging Parameter           ':'modules\\flexins\\fsm_module\\b6j.fsm',
	'MME/SGSN PRFIL Parameter       ':'modules\\flexins\\fsm_module\\woi.fsm',
	'MME/SGSN Network Parameter     ':'modules\\flexins\\fsm_module\\wvi.fsm',
	'MME Interface Parameter        ':'modules\\flexins\\fsm_module\\bii.fsm',
	'MME Timer Parameter            ':'modules\\flexins\\fsm_module\\bji.fsm',
	'MME/SGSN Specific Parameter    ':'modules\\flexins\\fsm_module\\ejh.fsm',
	'MME Overload Parameter         ':'modules\\flexins\\fsm_module\\bmo.fsm',
	'MME EMERGENCY Parameter        ':'modules\\flexins\\fsm_module\\bjf.fsm',
	'MME SECU and AUTH Parameter    ':'modules\\flexins\\fsm_module\\bsi.fsm'
}
paramstatus_str = u"""
NS Version:%(nsversion)s 
"""

parameter_get_commands = [
	("ZQNI;","show the NS general info"),
    ("ZWQO:CR;","show the NS packages information"),
    ("ZB6J;","show LTE paging parameter"),
    ("ZWOI;","show MME/SGSN PRFIL parameter"),
	("ZWVI;","show MME/SGSN Network parameter"),
	("ZBII;","show MME Interface parameter"),
	("ZBJI;","show MME Timer parameter"),
	("ZEJH;","show MME Specific parameter"),
	("ZBMO;","show MME Overload parameter"),
	("ZBJF;","show MME EMERGENCY parameter"),
	("ZBSI;","show MME SECU and AUTH parameter")
]



def read_block(logfile,blkname):
    loglines = file(logfile).readlines()

    return ''.join(loglines)

 
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

	info_result=[]
	#ns_parameter_values={name:'' for name in parameter_scripts}
	
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
    
	info_result.append(ns_version_status)
	logtxt = read_block(logfile,'NS_PARAMETER_CHECK')
    
    
	status = CheckStatus.UNCHECKED
    
	# From the logfile get Parameters
	for name,script in parameter_scripts.items():
		info_result.append(name)
		fsm = textfsm.TextFSM(open(script))
		fsminfos=fsm.ParseText(logtxt)
		if (len(fsminfos)>0):
			
			status = CheckStatus.PASSED
			for fsminfo in fsminfos: 
				info_result.append('\t'.join(fsminfo[0:]))
			info_result.append('\n')
			
	
	#print status
	if status == CheckStatus.UNCHECKED:
		status = CheckStatus.UNKNOWN

	#info_result=sorted(info_result)
	#print info_result

	result.update(status=status,info=info_result,error=error)
	return result
    
