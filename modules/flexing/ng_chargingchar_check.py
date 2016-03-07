# -*- coding: utf-8 -*-
"""Check the Charging character config for Huawei PCRF and CC=0 issue
When enable gx function, subscriber with CC=0 's GX CCR message will set th online and 
offline as disable and the charging mode decide by PCRF . But Huawei PCRF will return disable , so these subsciber(CC=0) will not generate CDR.
You can add the followed config to resolve the problem:
charchar-index = 0
charging-profile = charging-profile-1
other cc=1,2,3,5,6,7,9 can use the same way.
"""
import re
from libs.checker import ResultInfo,CheckStatus

## Mandatory variables 
##--------------------------------------------
module_id = '20160304.01'
tag  = ['flexing','china']
priority = 'critical'
name = "Verify the Charging character configuration in Session Profile"
desc = __doc__
criteria = "NG Charging character configuration have problem "
result = ResultInfo(name)
error = ''
##--------------------------------------------

##--------------------------------------------

##--------------------------------------------
## Optional variables
target_version = ['3.0','4.0','15.0']    

## first get the block of each 'show session-profile'
## from each block we will get the session-profile 's name and charging-index config 
pats_charchar = {'session-profile-block': re.compile(r"show ng session-profile (.*)\n(.* = .*(\n)+)+"), 
				 'session-profile-name': re.compile(r"session-profile-name = (.*)"),
				 'charchar-index': re.compile(r"charchar-index = 0"),
}
#charchar_str = "charchar-index = 0:%(charchar0)s
##

def read_block(logfile,blkname):
	loglines = file(logfile).readlines()

	return ''.join(loglines)


    
##--------------------------------------------
## Mandatory function: log_collection
##--------------------------------------------
def log_collection():
	cmds = ['show ng session-profile xxxxx-session-profile',
           ]
	for cmd in cmds:
		print cmd
        
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
	logtxt = read_block(logfile,'NG_Charing_status')
    
	charging_index_status=[]
	status = CheckStatus.UNCHECKED
    
	# Get every session-profile-block
	session_profile_block=[]
	pat=pats_charchar['session-profile-block']
	logtmp=logtxt
	r=pat.search(logtxt)
	while r<>None:
		session_profile_block.append(r.group())
		logtmp=logtmp[r.end():]
		r=pat.search(logtmp)
	
	# From each block get session-profile-name and charging-index info
	pat=pats_charchar['session-profile-name']
	for block in session_profile_block:
		r=pat.search(block)
		if r:
			session_profile_name=r.group(1)
			pat1=pats_charchar['charchar-index']
			r=pat1.search(block)
			if r:
				if status == CheckStatus.UNCHECKED:
					status = CheckStatus.PASSED
				charging_index_status.append(session_profile_name + ' have charchar-index=0')
			else:
				if status == CheckStatus.UNCHECKED:
					status = CheckStatus.FAILED
				charging_index_status.append(session_profile_name + ' have NOT charchar-index=0')
    
	if status == CheckStatus.UNCHECKED:
		status = CheckStatus.UNKNOWN
	
	result.load(status=status,info=charging_index_status,error=error)
	return result
    
