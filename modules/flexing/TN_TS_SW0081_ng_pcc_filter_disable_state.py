# -*- coding: utf-8 -*-
u"""检查PCC rule的pcc filter状态是否有'disable'的情况
当出现这种情况时，优先级在disable之后的所有filter都会被当作`disable`来对待。

适用版本: NG3.2, NG15
 - 该问题将在NG15 MP1 and NG3.2 3.0中修正

SOLUTION:
 - 使用fsclish删除不需要的filter,并且不要用disabled状态的pcc filter.
"""
import re
from libs.flexing import get_ng_version
from libs.checker import ResultInfo,CheckStatus

__author__ = 'wei.yao@huanuo-nokia.com'

## Mandatory variables
##--------------------------------------------
module_id = 'tn_ts_sw0081'
tag       = ['flexing','china']
priority  = 'critical'
name      = "Check PCC rule filter in disabled state"
desc      = __doc__
criteria  = u"There is PCC rule filter in DISABLE status"
result    = ResultInfo(name)
error     = ''
##--------------------------------------------


##--------------------------------------------
## Optional variables    
target_version = ['3.2','15']
## first get the block of each 'filter-state'

pats_stat = {'pcc-rule-cmd': re.compile(r"show ng service-awareness pcc-rule"),
'pcc-rule-name': re.compile(r"pcc-rule-name = (.*)"),
'filter-state-disable': re.compile(r"filter-state = disable"),
'filter-state-enable': re.compile(r"filter-state = enable")
}

check_commands = [
    ('@fsclish', "#below commands should be executed in fsclish shell."),
    ('show ng service-awareness pcc-rule *','## show service-awareness pcc-rule'),
]

def read_block(logfile,blkname):
    loglines = file(logfile).readlines()
    return ''.join(loglines)

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------    
def run(logfile):

    check_info = []

    loglines = file(logfile).readlines()
    logtxt = read_block(logfile,'pcc_rule')
	
    status = CheckStatus.UNCHECKED
	
    pat=pats_stat['pcc-rule-cmd']
    r=pat.search(logtxt)
    if r:
        if status == CheckStatus.UNCHECKED:
            status = CheckStatus.PASSED
    else:
        if status == CheckStatus.UNCHECKED:
            status = CheckStatus.UNKNOWN
            check_info.append(u'请检查PCC RULE的log是否已收集.')
            result.load(status=status,info=check_info,error=error)
        return result  
		
    pat_rulename = pats_stat['pcc-rule-name']
    pat_disable = pats_stat['filter-state-disable']
    pat_enable = pats_stat['filter-state-enable']
	
    line_count = len(loglines)
    line = 0
    while (line < line_count):
        r_pcc_name = pat_rulename.search(loglines[line])
        if r_pcc_name:
            curr_pcc_name=r_pcc_name.group(1)
            line = line + 1
            continue
        r_disable = pat_disable.search(loglines[line])
        if r_disable:
            r_enable = pat_enable.search(loglines[line+1])
            if r_enable:
                check_info.append(u'Rule Name: ' + curr_pcc_name + '\n')
                check_info.append(loglines[line])
                check_info.append(loglines[line+1])
                status = CheckStatus.FAILED
                line = line + 1
        line = line + 1
		
		
    result.load(status=status,info=check_info,error=error)
    return result