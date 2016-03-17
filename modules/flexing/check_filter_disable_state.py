"""Check the PCC rule filter in "disabled" state
VALIDITY: NG3.2, NG15
Correction for this issue will be provided in NG15 MP1 and NG3.2 3.0

SOLUTION
Use fsclish command ¡°unset¡± to completely remove unwanted filters from pcc-rule configuration and do not use filters in ¡°disabled¡± state.
"""
import re
from libs.flexing import get_ng_version
from libs.checker import ResultInfo,CheckStatus

## Mandatory variables
##--------------------------------------------
module_id = '20160311.01'
tag  = ['flexing','china']
priority = 'critical'
name = "Check PCC rule filter in disabled state"
desc = __doc__
criteria = "PCC rule filter in disabled state"
result = ResultInfo(name)
error = ''
##--------------------------------------------

##--------------------------------------------

##--------------------------------------------
## Optional variables    
target_version = ['3.2','15']
## first get the block of each 'filter-state'

pats_stat = {'filter-state-block': re.compile(r"filter-state = disable.*\n.*filter-state = enable")}
##

check_commands = [('show ng service-awareness pcc-rule *','## show service-awareness pcc-rule'),]

def read_block(logfile,blkname):
    loglines = file(logfile).readlines()
    return ''.join(loglines)

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

  check_info = []

	logtxt = read_block(logfile,'filter-state')

	status = CheckStatus.UNCHECKED

	pat=pats_stat['filter-state-block']

	r=pat.search(logtxt)
	if r:
		if status == CheckStatus.UNCHECKED:
		  status = CheckStatus.FAILED
			check_info.append('Check failed.')
	else:
		if status == CheckStatus.UNCHECKED:
		  status = CheckStatus.PASSED
			check_info.append('Check passed.')

	if status == CheckStatus.UNCHECKED:
		status = CheckStatus.UNKNOWN

	result.load(status=status,info=check_info,error=error)
	return result