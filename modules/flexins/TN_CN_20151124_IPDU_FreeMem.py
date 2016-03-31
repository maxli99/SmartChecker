# -*- coding: utf-8 -*-
u"""FlexiNS/MME IPDU空闲内存持续减少的问题

  -  NS/MME软件版本为NS3.15， NS3.15.1
  -  ACPI4-A& ACPI4-B

  解决方法：单元倒换或重启
"""
import re
from libs.checker import ResultInfo,CheckStatus

## Mandatory variables 
##-----------------------------------------------------
#check_id = '20160308.TN20151013'
module_id = 'TN-China-20151124'
tag       = ['flexins','china']
priority  = 'critical'
name      = "TN_CN_20151124_IPDU_FreeMem"
desc      = __doc__
criteria  = u"""\
(1)检查NS/MME软件版本为 ['N5 1.19-3','N5 1.17-5'] 或者更高版本.
(2) IPDU FREE MEMORY < 20%. 或者 
    IPDU 单元1143 告警 或者 
    lnx-mmeGTPLBS 模块占用内存较多>20%\
"""


## Optional variables
##-----------------------------------------------------
# available target versions:
target_versions = ['N5 1.19-3','N5 1.17-5']
check_commands = [
    ("ZWQO:CR;","show the VERSION in the MME/SGSN"),
	("ZAHO:;","show the alarms in the MME/SGSN"),
	("ZDOI:IPDU,(active):M;","show the memory of active IPDU ."),
	("ZDDE:IPDU,(active):\"top -n1\";","show the memory usage of process lnx-mmeGTPLBS in active IPDU .")
]
know_version_identify_Patt = r"\s*(N\d+\s+\d+.\d+-\d+)\s*"
##-----------------------------------------------------
##version_up_NS15_id('N5 1.17-5')
def version_up_NS15_id(NsVersionId):
	up_id = 0
	version_id_Patt = r"\s*N(\d+)\s+\d+.\d+-\d+\s*"
	m=re.search(version_id_Patt,NsVersionId)
	if m:
		big_version_id = m.group(1)
		if int(big_version_id) >= 5:
			up_id =1
	return up_id
			

def is_NS15_version_id(NsVersionId,Ns15VersionList):
	if NsVersionId in Ns15VersionList:
		return 1
	else:
		return 0

def Find_NS_MME_Patt_Return_Info_List(LogFile,CommandStr,InfoPatt,ReturnInfoLen):
	Command_start=False
	Command_end=False
	return_info_list=[]
	Command_start_Patt=r"\s*[Z]?%s\s*" % (CommandStr)
	Command_start_Patt=Command_start_Patt.replace(':;','[:]?;')
##	print "Command_start_Patt =",Command_start_Patt
	Command_end_Patt=r"\s*COMMAND\s+EXECUTED\s*$"
	Find_Info_Patt=InfoPatt
##	print "Find_Info_Patt =",Find_Info_Patt
	return_Len = ReturnInfoLen+1
	fp=open(LogFile,'r')
	
	for line in fp.readlines():
		if Command_start==False and Command_end==False:
			m=re.search(Command_start_Patt,line)
			if m:
				Command_start=True
				continue
		elif Command_start==True and Command_end==False:
			m0=re.search(Command_end_Patt,line)
			m1=re.search(Find_Info_Patt,line)
			if m0:
				Command_end=True
				continue
			if m1:
##				print "line =",line
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

def F_MME_Patt_Return_Info_List(LogFile,CommandStr,InfoPatt1,Deviation=0,InforPatt2="",groupid1=0,groupid2=0):
	""" 
	1，
	2，如果Deviation=0，但 InforPatt2《》“”，标明只要在命令开始后找到InforPatt2即可，不考虑位置, 待实现
	3，groupid[0]是指InfoPatt1 匹配后返回的哪个group,groupid[1]是InforPatt2匹配后返回的group
	"""
	Command_start=False
	Command_end=False
	m=None
	m0=None
	m1=None
	m2=None
	m_first=None
	m_second=None
	
	return_info_list=[["UNHIT","0"],["","0"],["","0"]]
	#DDE:IPDU,0:"top -n1",;
	Command_start_Patt=r"\s*[Z]?%s\s*" % (CommandStr)
	Command_start_Patt=Command_start_Patt.replace(':;','[:]?;')
##	print "Command_start_Patt =",Command_start_Patt
	Command_end_Patt=r"\s*COMMAND\s+EXECUTED\s*$"
	Find_Info_Patt=InfoPatt1
##	print "Find_Info_Patt =",Find_Info_Patt
	#return_Len = ReturnInfoLen+1

	fp=open(LogFile,'r')

        LogLines=fp.readlines()
	i=-1
	for line in LogLines:
		i=i+1

		if Command_start==False and Command_end==False:
			m=re.search(Command_start_Patt,line)
			if m:
				Command_start=True
				continue
		elif Command_start==True and Command_end==False:
		#command begining but not finished
			m0=re.search(Command_end_Patt,line)
			
			if m0:
				#command finished
				Command_end=True
				break
			#13198 root      20   0  620m 291m 3584 S 70.6  1.2   9363:13 lnx-mmeGTPLBS
			m1=re.search(Find_Info_Patt,line)
			
			if m1:
				#The first pattern hit, check the seconde pattern in deviation line
				return_info_list[0][0]="HIT"
				m_first=m1.group(0)
				if m1.group(0) : return_info_list[1][0]=m1.group(0)
				if groupid1<>0 : return_info_list[1][1]=m1.group(groupid1)
				
				if Deviation<>0:					
					m2=re.search(InforPatt2,LogLines[i+Deviation])
					if m2 : 
						m_second=m2.group(0)
						if m_second : return_info_list[2][0]=m2.group(0)
						if groupid2<>0 : return_info_list[2][1]=m1.group(groupid2)

	#if m_first : return_info_list.append(m_first)
	#if m_second : return_info_list.append(m_second)
	fp.close()
	return return_info_list


def returnNotMatchItemInList(List_two,ItemName):
	ItemName_New = ''
	for item_name in List_two:
		if item_name != ItemName:
			ItemName_New = item_name
	return ItemName_New

## Mandatory function: run
def run(logfile):
	result = ResultInfo(name,priority=priority)
	info   = []
	errmsg = ''
	Ns_version_Patt=r"\s*\S+\s+BU\s+\S+\s+(\w+\d+\s*\S+)\s+Y\s+Y\s*$"
	abnormal_flag=0
	
	try :
		version = Find_NS_MME_Patt_Return_Info_List(logfile,'WQO:CR;',Ns_version_Patt,1)[0]
	except IndexError:
		version = ''
##	print "\n****Find version id is : ",version
	if is_NS15_version_id(version,target_versions)>0 or version_up_NS15_id(version)>0:
		result.status = CheckStatus.PASSED
		info.append(u"    - 检查到 NS/MME 软件版本为：'%s' ,它属于或者高于NS15版本." % version)
	else:
		m=re.search(know_version_identify_Patt,version)
		if m:
			result.status = CheckStatus.FAILED
			info.append(u"    - 检查到 NS/MME 软件版本为：'%s' ,它不属于或者低于NS15版本." % version)
		else:
			result.status = CheckStatus.UNKNOWN
			info.append(u"    - 检查到 NS/MME 软件版本为：'%s' ,它不属于NS/MME主流版本,请手动确认版本信息." % version)
			if version == '':
				errmsg = ' Have not find NS Version release identification !!'
		result.update(info=info,error=errmsg)
		return result

        #条件一 IPDU FREE MEMORY >20%
	#ZDOI:IPDU,0:M;
	#FREE MEMORY 2265 39
	CommandPatt=r"DOI:IPDU,\d{1}:M:+;"
	
	InfoPatt1=r"^\s*FREE MEMORY\s+\S+\s+(\S+)\s*$"	
	InfoPatt2=r""
	
	try:
		MME_Usage = F_MME_Patt_Return_Info_List(logfile,CommandPatt,InfoPatt1,0,InfoPatt2,1,0)
	except IndexError:
		MME_Usage[0][0] = "Unkown Error!"
		MME_Usage[0][1] = -1

	if MME_Usage[0][0] =="HIT" :
		if float(MME_Usage[1][1])<20 :
			abnormal_flag=1
			info.append(u"    - 检查到 NS/MME IPDU 空闲内存存量过低 ."+MME_Usage[1][1])
		else:
			info.append(u"    - 检查到 NS/MME IPDU 空闲内存存量在门限范围: "+MME_Usage[1][1])
	elif MME_Usage[0][0] =="UNHIT" :
		
		info.append(u"    - 没有检查到特征字符串.")
	else:
		abnormal_flag=-1
		info.append(u"    - 检查过程中异常错误，结果未知。 Unknown Result.")
			
        #条件二 ，IPDU 告警1143
	"""
        <HIST> SHMME03BNK IPDU-0 SWITCH 2015-11-01 02:13:02.99
        * DISTUR IPDU-0 1A001-00-5 CPUPRO
        (6270) 1143 AMOUNT OF FREE MEMORY REDUCED
        00000000 00032000 00031A4C 00593DD0
        """
	
	InfoPatt_mapping1=r"\s*1143\s+AMOUNT OF FREE MEMORY REDUCED"
	InfoPatt_mapping2=r"IPDU-"
	try:
		MME_Alarm_1143 = F_MME_Patt_Return_Info_List(logfile,'AHO:;',InfoPatt_mapping1,-1,InfoPatt_mapping2)
	except IndexError:
		MME_Alarm_1143[0][0] = "Unkown Error!"
		MME_Alarm_1143[0][1] = -1

	if MME_Alarm_1143[0][0] =="HIT":
		
                abnormal_flag=1
		info.append(u"    - 检查到 NS/MME 1143 AMOUNT OF FREE MEMORY REDUCED 告警.")
	elif MME_Alarm_1143[0][0] =="UNHIT":
		
		info.append(u"    - 检查到 NO Alarm 1143.")		
	else:
		abnormal_flag=-1
		info.append(u"    - 检查到过程中异常错误，结果未知。 Unknown Result.")

        
        #条件三 IPDU lnx-mmeGTPLBS 进程内存利用 < 20%
	CommandPatt=r"DDE:IPDU,\d{1}:\"top -n1\",;"
	
	#11965 root 20 0 554m 231m 3500 S 9.9 4.0 3476:31 lnx-mmeGTPLBS
	InfoPatt1=r"^.*\s+(\S+)\s+\S+\s+lnx-mmeGTPLBS"
	InfoPatt2=r""
	try:
		MME_Usage = F_MME_Patt_Return_Info_List(logfile,CommandPatt,InfoPatt1,0,InfoPatt2,1,0)
	except IndexError:
		MME_Usage[0][0] = "Unkown Error!"
		MME_Usage[0][1] = -1

	if MME_Usage[0][0] =="HIT" :
		if float(MME_Usage[1][1])>20 :
			abnormal_flag=1
			info.append(u"    - 检查到 NS/MME slnx-mmeGTPLBS 内存占用过高 ."+MME_Usage[1][1])
		else:
			info.append(u"    - 检查到 NS/MME slnx-mmeGTPLBS 内存占用在门限范围: "+MME_Usage[1][1])
	elif MME_Usage[0][0] =="UNHIT" :
		
		info.append(u"    - 没有检查到特征字符串.")
	else:
		abnormal_flag=-1
		info.append(u"    - 检查过程中异常错误，结果未知。 Unknown Result.")
		
        if abnormal_flag==-1:
		result.status = CheckStatus.UNKNOWN
	
	elif abnormal_flag==1 :
		
		result.status = CheckStatus.FAILED
	else:
		result.status = CheckStatus.PASSED

	info=[line+'\n' for line in info]
	result.update(info=info,error=errmsg)
	return result



