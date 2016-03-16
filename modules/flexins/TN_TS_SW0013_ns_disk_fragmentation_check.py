"""Check the NS Harddisk fragment status
Before MME/SGSN upgrade or when we find the operation on MME/SGSN become slowly,we 'd better check the harddisk have fragment issue. 
"""
import re
from libs.checker import ResultInfo,CheckStatus

## Mandatory variables 
##--------------------------------------------
module_id = '20160228.01'
tag  = ['flexins','china']
priority = 'critical'
name = "Verify the Disk fragmentation problem in FNS"
desc = __doc__
criteria = "NS fragment status is (normal,abnormal)"
result = ResultInfo(name)
error = ''
##--------------------------------------------

##--------------------------------------------

##--------------------------------------------
## Optional variables
target_version = 3.0-15.0    

pats_fragment = {'OMU-WDU0': re.compile(r"ZDDE:OMU.*?WDU-0.*?Fragmentation degree ",re.S),
		'OMU-WDU1': re.compile(r"ZDDE:OMU.*?WDU-1.*?Fragmentation degree ",re.S),
		'MCHU-WDU0': re.compile(r"ZDDE:MCHU.*?WDU-0.*?Fragmentation degree ",re.S),
		'MCHU-WDU1': re.compile(r"ZDDE:MCHU.*?WDU-1.*?Fragmentation degree ",re.S),
}
fragmentstatus_str = "OMU(WDU-0):%(OMU-WDU0)s, OMU(WDU-1):%(OMU-WDU1)s, MCHU(WDU-0):%(MCHU-WDU0)s, MCHU(WDU-1):%(MCHU-WDU1)s"
##

def read_block(logfile,blkname):
	loglines = file(logfile).readlines()

	return ''.join(loglines)

def hardwareinfo():
	hwinfo = {}
	return hwinfo
    
def get_card(caretype):
	return 
##--------------------------------------------
## Mandatory function: log_collection
##--------------------------------------------
def log_collection():
	cmds = ['ZDDE:OMU:"ZMA:W0,F3,,,,,","ZMA:W1,F3,,,,,","ZGSC:,00FC";',
            'ZDDE:MCHU:"ZMA:W0,F3,,,,,","ZMA:W1,F3,,,,,","ZGSC:,00FC";',
            ]
	for cmd in cmds:
		print cmd
        
##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):
	logtxt = read_block(logfile,'NS_fragment_status')
    
	fragment_status={name:'' for name in pats_fragment}
	status = CheckStatus.UNCHECKED
    
	for name,pat in pats_fragment.items():
		r=pat.search(logtxt)
		#print r.end()
		if r:
			logpos=r.end()
			if status == CheckStatus.UNCHECKED:
				status = CheckStatus.PASSED
			fragment_status[name] = logtxt[logpos:logpos+5]
			if fragment_status[name] > '60.0':
				status = CheckStatus.FAILED
			#else:
			#	status = CheckStatus.PASSED
    
    #print ntpstatus_str, ntpstatus
	if status == CheckStatus.UNCHECKED:
		status = CheckStatus.UNKNOWN
	#result.load(status=status,info=[fragmentstatus_str % fragment_status],error=error)
	result.load(status=status,info=[fragmentstatus_str % fragment_status],error=error)
	return result
    