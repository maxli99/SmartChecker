# -*- coding: utf-8 -*-
"""Check if memory leaks in FlexiNG AS/SAB nodes
VALIDITY: NG3.1, NG3.2
"""
import re
from libs.checker import CheckStatus,ResultInfo
from libs.flexing import get_ng_version
from libs.tools import MessageBuffer

## Mandatory variables 
##--------------------------------------------
module_id = 'NG20150518.01'
name      = "memory_leak"
version   = '1.0'
desc      = __doc__
tags      = ['flexing','china']
priority  = 'critical'

mem_threshold = {'AS':110,'SAB':500}  #MB
criteria      = "memory usage: AS < %(AS)sMB or SAB < %(SAB)sMB" % mem_threshold
##--------------------------------------------

## Optional variables
   
pat_memfail = re.compile("ssh ([\w\d-]+) showstat\|.*?mem_alloc_failed_for_linear_filters = (\d+)",re.DOTALL)
pat_memallo = re.compile("info ([\w\d-]+) featuremem.*FASTPATH_MALLOC dynamic allocated bytes \[chunks\]: (\d+)/(\d+)")

logline_format = "    - %s"
##

def check_memory_fail_counter(loglines):
    _logblk=''.join(loglines)
    status = CheckStatus.UNKNOWN
    info = MessageBuffer(lineformat=logline_format)
    error = ''
    
    _results = pat_memfail.findall(_logblk)
    for node,cnt in set(_results):
        if int(cnt) > 0:
            status = CheckStatus.FAILED
            info.append("** %s has %s times memory failed." % (node,cnt))
    
    return status,info.buffer,error

def check_memory_allocation(loglines):
    status = CheckStatus.UNKNOWN
    flag_fail = False
    flag_passed = False
    info = MessageBuffer(lineformat=logline_format)
    error = ''
    _mem = {'AS':[],'SAB':[]}
    
    for line in loglines:  
        r2 = pat_memallo.search(line)
        if r2:
            mem = int(r2.groups()[1])/1024.0/1024.0
            node = r2.groups()[0]
            node_type = re.sub('[\d+-]','',node)
            _mem[node_type].append((node,mem))
            #print "mem allocated!",node,mem,node_type,mem_threshold[node_type]
            if mem > mem_threshold[node_type]:
                flag_fail = CheckStatus.FAILED
                info.append('%s memory is closing to full: %.5s MB\n' %(node, mem))
            else:
                flag_passed = CheckStatus.PASSED
                info.append("%s memory: %s\n" %(node,mem))

    status = (flag_fail or flag_passed) or CheckStatus.UNKNOWN
    
    if status == CheckStatus.UNKNOWN:
        info.append("Can't found the memory usage info.")        
    if status !=CheckStatus.FAILED:
        for ntype,memlist in _mem.items():
            if len(memlist) == 0: continue
            maxmem=sorted(memlist,key=lambda x:x[1],reverse=True)[0]
            info.append('%s has a max memory %.6s MB\n' % maxmem) 

    return status,info.buffer,error
    
## Mandatory function: run
def run(logfile, *args,**kwargs):
    "this function execute the check steps and return "
    loglines = file(logfile).readlines()
    result = ResultInfo(name)
    info = []
    error = ''
    
    # check the NG version first.
    ngversion=get_ng_version(logfile)

    if not ngversion:  # not version info found.
        #status = CheckStatus.UNKNOWN
        info.append("    - NG version can't be determindated.")
        #error = "NG version is not found."

    elif ngversion[0][:3] == '3.2':
        status,info,error = check_memory_fail_counter(loglines)
        if status == CheckStatus.FAILED and len(info)>0:
            result.status = status
    

    ## check function 2
    status,_info,error = check_memory_allocation(loglines)

    info.append(''.join(_info))
    #result.status = status

    result.update(status=status,info=info,error=error)
    return result