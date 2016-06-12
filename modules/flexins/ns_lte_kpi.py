# -*- coding: utf-8 -*-

u"""
 计算MME的LTE相关KPI指标
"""

import re
from libs.checker import ResultInfo,CheckStatus
from libs.flexins import FlexiNS
from libs.flexins import get_ns_version
from libs.infocache import shareinfo


## Mandatory variables 
##--------------------------------------------
module_id = 'NSKPI'
tag       = ['flexins','china']
priority  = 'major'
name      = u"NS LTE KPI"
desc      = __doc__
criteria  = u"""
（1）检查MME/SGSN版本为 ['N5 1.19-3','N5 1.17-5'] 或者更高版本。
（2）按照log中的Counter值，计算KPI。
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

pats_counters = {'Counter': re.compile(r"(M[\d]+C[\d]+)[\s]+(.*)([\d]{10})\n",re.M)
}
#fragmentstatus_str = "NS Version:%(nsversion)s, OMU(WDU-0):%(OMU-WDU0)s, OMU(WDU-1):%(OMU-WDU1)s, MCHU(WDU-0):%(MCHU-WDU0)s, MCHU(WDU-1):%(MCHU-WDU1)s"
##
kpi_formula = {
	'ATTACH Succ Ratio (%)           ':['GS:round($0$/($0$+$1$),4)*100','M50C000','M50C001'],
	'PDN Activate Succ Ratio (%)     ':['GS:round($0$/($0$+$1$),4)*100','M51C000','M51C001'],
	'IMS PDN Activate Succ Ratio (%) ':['GS:round($0$/($0$+$1$),4)*100','M51C048','M51C049'],
	'Paging Succ Ratio (%)           ':['GS:round($0$/($0$+$1$),4)*100','M50C012','M50C013'],
	'TAU Succ Ratio (%)              ':['GS:round($0$/($0$+$1$),4)*100','M50C035','M50C036'],
	'InterSYS TAU Succ Ratio (%)     ':['GS:round($0$/($0$+$1$),4)*100','M50C041','M50C042'],
	'Auth Succ Ratio (%)             ':['GS:round($0$/($0$+$1$+$2$),4)*100','M54C000','M54C001','M54C002'],
	'COMBIND ATTACH Succ Ratio (%)   ':['GS:round($0$/($0$+$1$),4)*100','M50C045','M50C048'],
	'COMBIND TAU Succ Ratio (%)      ':['GS:round($0$/($0$+$1$),4)*100','M50C035','M50C036'],
	'Service Request Succ Ratio (%)  ':['GS:round($0$/($0$+$1$),4)*100','M50C007','M50C008'],
	'IntraMME X2 Succ Ratio (%)      ':['GS:round($0$/($0$+$1$),4)*100','M50C009','M50C010'],
	'IntraMME S1 Succ Ratio (%)      ':['GS:round($0$/($0$+$1$),4)*100','M50C019','M50C020'],
	'InterMME OUT S1 Succ Ratio (%)  ':['GS:round($0$/($0$+$1$),4)*100','M50C067','M50C071'],
	'InterMME IN S1 Succ Ratio (%)   ':['GS:round(($0$+$2$)/($0$+$1$+$2$),4)*100','M50C066','M50C070','M50C132']
#	'InterMME TAU Succ Ratio':['GS:round($0$/($0$+$1$),4)*100','M50C035','M50C036']
}
kpistatus_str = u"""
NS Version:%(nsversion)s 
"""

counter_get_commands = [
    ("ZWQO:CR;","show the NS packages information"),
    ("ZTPP:MMMT;","show MMMT counter"),
    ("ZTPP:SMMT;","show SMMT counter"),
]
value_counters = {}

counterlist=['M72C012','M72C014','GS:4,5:(round($4$/($4$+$5$),4)*100)','M72C013','M72C015','GS:7,8:(round($7$/($7$+$8$),4)*100)','M72C000','M72C001','M72C002','M72C003']

def getKPIvalue(kpi_name,kpi_func_param,value_counters):
	# Get the param length, if 0, error ,if 1 ,mean kpi = counter
	# if 2 or larger, mearn kpi = eval(counter1,counter2,......)
	k=len(kpi_func_param)
	if (k==0):
		return None
	elif (k==1):
		if (value_counters[kpi_func_param[0]])<>None:
			return value_counters[kpi_func_param[0]]
		else:
			return None

	# the formula string sample: 'GS:4,5:round($4$/($4$+$5$),4)*100'
	kpi_formula=kpi_func_param[0]
	#print 'kpi_formula='+kpi_formula
	kpi_formula_struc=kpi_formula.split(':')
	if ((len(kpi_formula_struc)==0) or kpi_formula_struc[0]<>'GS'):
		return None
	
	gs_desc=kpi_formula_struc[1]
	#print 'gs_desc='+gs_desc
	gs_counters_list=kpi_func_param[1:]
	#print gs_counters_list
	items_counter=len(gs_counters_list)
	itemno=0
	for item in gs_counters_list:
	#print item
		#gs_item=gs_desc.replace('$'+item+'$',str(value_counters[gs_counters_list(item-1)]))
		#print 'gs_counters_list[itemno]='+gs_counters_list[itemno]
		#print 'value_counters[gs_counters_list[itemno]]='+value_counters[gs_counters_list[itemno]]
		if (value_counters[gs_counters_list[itemno]])==None:
			return None
		gs_desc=gs_desc.replace('$'+str(itemno)+'$',str(float(value_counters[gs_counters_list[itemno]])))
		#print 'gs_real real:'+gs_realitem
		itemno=itemno+1
	try:
		#print 'gs_desc='+gs_desc
		gs_result=eval(gs_desc)
		#print 'gs_result='+str(gs_result)
	except:
		gs_result=0
	
	#print gs_result		
	return gs_result



def read_block(logfile,blkname):
    loglines = file(logfile).readlines()

    return ''.join(loglines)

 
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

	info_result=[]
	ns_kpi_values={name:'' for name in kpi_formula}
	
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
	logtxt = read_block(logfile,'NS_KPI_CHECK')
    
    
	status = CheckStatus.UNCHECKED
    
	# From the KPI logfile get Counters
	for name,pat in pats_counters.items():
		if(name=='Counter'):
			r=pat.search(logtxt)
			#print r.end()
			while r:
				logpos=r.end()
				if status == CheckStatus.UNCHECKED:
					status = CheckStatus.PASSED
				#print 'Counter: '+r.group(1)+';'+ '='+ r.group(3)
				value_counters[r.group(1)] = r.group(3)
				logtxt=logtxt[logpos:]
				r=pat.search(logtxt)
				
	# According the KPI formula get the KPI Value
	for kpi_name in kpi_formula.keys():
		kpi_func_param = kpi_formula[kpi_name]
		kpi_value = getKPIvalue(kpi_name,kpi_func_param,value_counters)
		info_result.append(kpi_name+' = \t\t'+str(kpi_value))
	
	#print fragementstatus_str, fragment_status
	if status == CheckStatus.UNCHECKED:
		status = CheckStatus.UNKNOWN

	info_result=sorted(info_result)
	#print info_result

	result.update(status=status,info=info_result,error=error)
	return result
    