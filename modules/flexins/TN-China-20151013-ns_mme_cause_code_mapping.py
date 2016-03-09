# -*- coding: utf-8 -*-
"""FlexiNS/MME Cause code mapping Checking
     -  NS/MME软件版本为NS15或者更高版本
     -  已开启功能开关PRFILE002:2244-MME_CC_MAPPING_ENABLED
     -  有新建CAUSE CODE SETS,如:EPCEMM和EPCESM(各项目名称可能不相同).
     -  EPCEMM,TYPE=EMM,PROC=ATTREJ,INTCAUSE=142 To EXTERNAL CAUSE=15
     -  EPCEMM,TYPE=EMM,PROC=ATTREJ,INTCAUSE=96 To EXTERNAL CAUSE=7
     -  EPCESM,TYPE=ESM,PROC=PDNCR,INTCAUSE=165 To EXTERNAL CAUSE=33

"""
import re
from libs.checker import ResultInfo,CheckStatus

## Mandatory variables 
##-----------------------------------------------------
#check_id = '20160308.TN20151013'
module_id = 'TN-China-20151013'
tag = ['flexins','china']
priority = 'intermediate'
name = "TN-China-20151013-ns_mme_cause_code_mapping"
desc = __doc__
criteria = "(1)检查NS/MME软件版本为 ['N5 1.19-3','N5 1.17-5'] 或者更高版本.\n\
          (2)开启功能开关PRFILE002:2244-MME_CC_MAPPING_ENABLED.\n\
          (3)新建CAUSE CODE SETS 满足下面条件,如:EPCEMM和EPCESM：\n\
             -EPCEMM,TYPE=EMM,PROC=ATTREJ,INTCAUSE=142 To EXTERNAL CAUSE=15\n\
             -EPCEMM,TYPE=EMM,PROC=ATTREJ,INTCAUSE=96 To EXTERNAL CAUSE=7\n\
             -EPCESM,TYPE=ESM,PROC=PDNCR,INTCAUSE=165 To EXTERNAL CAUSE=33\n\
"
##-----------------------------------------------------

## Optional variables
##-----------------------------------------------------
# available target versions:
target_versions = ['N5 1.19-3','N5 1.17-5']
check_commands = [
	("ZWOI:;","show the NS data of the parameters defined in the PRFILE"),
	("ZWQO:CR;","show the NS packages information"),
	("ZKAL:;","show the NS cause code set names"),
	("ZKAL:NAME=EPCEMM,TYPE=EMM,PROC=ATTREJ,INTCAUSE=142:;","show the NS cause code set EPCEMM information,You can change the cause code set name for your project"),
	("ZKAL:NAME=EPCEMM,TYPE=EMM,PROC=ATTREJ,INTCAUSE=96:;","show the NS cause code set EPCEMM information,You can change the cause code set name for your project"),
	("ZKAL:NAME=EPCESM,TYPE=ESM,PROC=PDNCR,INTCAUSE=165:;","show the NS cause code set EPCESM information,You can change the cause code set name for your project")
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
##					print "m1.group(%s) =" % (infoId), m1.group(infoId)
					if m1.group(infoId):
						return_info_list.append(m1.group(infoId))
					else:
						return_info_list.append('Not_Find_Infomation')
				continue
		else:
			break
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
	result = ResultInfo(name)
	info   = []
	errmsg = ''
	Ns_version_Patt=r"\s*\S+\s+BU\s+\S+\s+(\w+\d+\s*\S+)\s+Y\s+Y\s*$"
	version = Find_NS_MME_Patt_Return_Info_List(logfile,'WQO:CR;',Ns_version_Patt,1)[0]
##	print "\n****Find version id is : ",version
	if is_NS15_version_id(version,target_versions)>0 or version_up_NS15_id(version)>0:
		result.status = CheckStatus.PASSED
		info.append("    - 检查到 NS/MME 软件版本为：'%s' ,它属于或者高于NS15版本." % version)
	else:
		m=re.search(know_version_identify_Patt,version)
		if m:
			result.status = CheckStatus.FAILED
			info.append("    - 检查到 NS/MME 软件版本为：'%s' ,它不属于或者低于NS15版本." % version)
		else:
			result.status = CheckStatus.UNKNOWN
			info.append("    - 检查到 NS/MME 软件版本为：'%s' ,它不属于NS/MME主流版本,请手动确认版本信息." % version)
			if version == '':
				errmsg = ' Have not find NS Version release identification !!'
		result.update(info=info,error=errmsg)
		return result
	
	InfoPatt_mapping=r"\s*02244\s+MME_CC_MAPPING_ENABLED\s+(\S+)\s+YESs*$"
	MME_CC_MAPPING_ENABLED_Value = Find_NS_MME_Patt_Return_Info_List(logfile,'WOI:;',InfoPatt_mapping,1)[0]
##	print "MME_CC_MAPPING_ENABLED_Value = ",MME_CC_MAPPING_ENABLED_Value
	if int(MME_CC_MAPPING_ENABLED_Value) == 1:
		result.status = CheckStatus.PASSED
		info.append("    - 检查到 NS/MME 功能开关PRFILE002:2244-MME_CC_MAPPING_ENABLED已开启.")
	else:
		result.status = CheckStatus.FAILED
		info.append("    - 检查到 NS/MME 功能开关PRFILE002:2244-MME_CC_MAPPING_ENABLED未开启.")
		result.update(info=info,error=errmsg)
		return result
	EPCEMM_Patt = r"\s*(\S*)\s+EMM\s*$"
	EPCESM_Patt = r"\s*(EPCESM)\s+ESM\s*$"
	Cause_code_set_EMM_Name_List = Find_NS_MME_Patt_Return_Info_List(logfile,'KAL:;',EPCEMM_Patt,1)
	Cause_code_set_ESM_Name_List = Find_NS_MME_Patt_Return_Info_List(logfile,'KAL:;',EPCESM_Patt,1)
	Cause_code_set_EPCEMM = returnNotMatchItemInList(Cause_code_set_EMM_Name_List,'EMMDEF')
	Cause_code_set_EPCESM = returnNotMatchItemInList(Cause_code_set_ESM_Name_List,'ESMDEF')

##	print "Cause_code_set_EPCEMM = ",Cause_code_set_EPCEMM
##	print "Cause_code_set_EPCESM = ",Cause_code_set_EPCESM
	
	EmmIntcause142_Patt = r"\s*EXTERNAL\s+CAUSE\s+:\s+(\d+)\s*$"
	EmmIntcause96_Patt = r"\s*EXTERNAL\s+CAUSE\s+:\s+(\d+)\s*$"
	EsmIntcause165_Patt = r"\s*EXTERNAL\s+CAUSE\s+:\s+(\d+)\s*$"
	
	EmmIntcause142_Command = 'KAL:NAME=%s,TYPE=EMM,PROC=ATTREJ,INTCAUSE=142:;' % (Cause_code_set_EPCEMM)
	EmmIntcause96_Command = 'KAL:NAME=%s,TYPE=EMM,PROC=ATTREJ,INTCAUSE=96:;' % (Cause_code_set_EPCEMM)
	EsmIntcause165_Command = 'KAL:NAME=%s,TYPE=ESM,PROC=PDNCR,INTCAUSE=165:;' % (Cause_code_set_EPCESM)
	
	EmmExternal142 = Find_NS_MME_Patt_Return_Info_List(logfile,EmmIntcause142_Command,EmmIntcause142_Patt,1)[0]
	EmmExternal96= Find_NS_MME_Patt_Return_Info_List(logfile,EmmIntcause96_Command,EmmIntcause96_Patt,1)[0]
	EsmExternal165 = Find_NS_MME_Patt_Return_Info_List(logfile,EsmIntcause165_Command,EsmIntcause165_Patt,1)[0]
##	print "EmmExternal142 = ",EmmExternal142
##	print "EmmExternal96 = ",EmmExternal96
##	print "EsmExternal165 = ",EsmExternal165
	
	if int(EmmExternal142) == 15 and int(EmmExternal96) == 7 and int(EsmExternal165) == 33 :
		result.status = CheckStatus.PASSED
		info.append("    - 检查到 NS/MME 的CAUSE CODE SETS: %s,TYPE=EMM,PROC=ATTREJ,INTCAUSE=142 To EXTERNAL CAUSE=%s" % (Cause_code_set_EPCEMM,EmmExternal142))
		info.append("    - 检查到 NS/MME 的CAUSE CODE SETS: %s,,TYPE=EMM,PROC=ATTREJ,INTCAUSE=96 To EXTERNAL CAUSE=%s" % (Cause_code_set_EPCEMM,EmmExternal96))
		info.append("    - 检查到 NS/MME 的CAUSE CODE SETS: %s,,TYPE=ESM,PROC=PDNCR,INTCAUSE=165 To EXTERNAL CAUSE=%s" % (Cause_code_set_EPCESM,EsmExternal165))
	else:
		result.status = CheckStatus.FAILED
		info.append("    - 检查到 NS/MME 的CAUSE CODE SETS: %s,TYPE=EMM,PROC=ATTREJ,INTCAUSE=142 To EXTERNAL CAUSE=%s" % (Cause_code_set_EPCEMM,EmmExternal142))
		info.append("    - 检查到 NS/MME 的CAUSE CODE SETS: %s,,TYPE=EMM,PROC=ATTREJ,INTCAUSE=96 To EXTERNAL CAUSE=%s" % (Cause_code_set_EPCEMM,EmmExternal96))
		info.append("    - 检查到 NS/MME 的CAUSE CODE SETS: %s,,TYPE=ESM,PROC=PDNCR,INTCAUSE=165 To EXTERNAL CAUSE=%s" % (Cause_code_set_EPCESM,EsmExternal165))

	result.update(info=info,error=errmsg)
	return result
