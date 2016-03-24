# -*- coding: utf-8 -*-
u"""由于有NG3.x 版本SAEGW的AS/SAB存在内存泄露的问题，导致发生终端用户上网困难等多种症状非常多样，
需要对SAE经常检查内存是否泄露。
"""
import re
from libs.checker import CheckStatus,ResultInfo
from libs.infocache import shareinfo
from libs.tools import MessageBuffer

__author__ = 'Liu Jun'
__email__ = 'jun1.liu@nokia.com'
__date__ = '20160315'

## Mandatory variables 
##--------------------------------------------
module_id = 'NG20150518.01'
name      = "FlexiNG(NG3.x) AS/SAB Memory leak Check"
version   = '1.0'
desc      = __doc__
tags      = ['flexing','china']
priority  = 'critical'

mem_threshold = {'AS':110,'SAB':500}  #MB
criteria      = u"""
FlexiNG NG3.1/NG3.2, 正常的内存利益率: AS < %(AS)sMB or SAB < %(SAB)sMB

解决方案：
  1. 有条件关闭 hicut 的项目就关闭（因为关闭 hitcut 会导致 Node 负荷小幅增加，需要提前检查 CPU 使用情况）。
  2. 没有条件关 hitcut 的项目，必需要把检查内存利用率的操作列入日常的维护计划
""" % mem_threshold


## Optional variables 
pat_memfail = re.compile("ssh ([\w\d-]+) showstat\|.*?mem_alloc_failed_for_linear_filters = (\d+)",re.DOTALL)
pat_memallo = re.compile("info ([\w\d-]+) featuremem.*FASTPATH_MALLOC dynamic allocated bytes \[chunks\]: (\d+)/(\d+)")
target_version = ['3.1','3.2']
logline_format = "    - %s\n"

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
                info.append('%s memory is closing to full: %.5s MB' %(node, mem))
            else:
                flag_passed = CheckStatus.PASSED
                info.append("%s memory: %s" %(node,mem))

    status = (flag_fail or flag_passed) or CheckStatus.UNKNOWN
    
    if status == CheckStatus.UNKNOWN:
        info.append("Can't found the memory usage info.")        
    if status !=CheckStatus.FAILED:
        for ntype,memlist in _mem.items():
            if len(memlist) == 0: continue
            maxmem=sorted(memlist,key=lambda x:x[1],reverse=True)[0]
            info.append('%s has a max memory %.6s MB' % maxmem) 

    return status,info.buffer,error
    
## Mandatory function: run
def run(logfile, *args,**kwargs):
    "this function execute the check steps and return "
    loglines = file(logfile).readlines()
    result = ResultInfo(name)
    info = []
    error = ''
    
    ng = shareinfo['FlexiNG']

    # check the NG version first.
    if not ng.version:  # not version info found.
        #status = CheckStatus.UNKNOWN
        info.append(logline_format % "NG version can't be determindated.")
        
    else:
        match = ng.match_version(major=target_version)

        if match['major']:
            status,info,error = check_memory_fail_counter(loglines)
            if status == CheckStatus.FAILED and len(info)>0:
                result.status = status
        else:
            major_version = ng.version['major']
            info.append(logline_format % ("The TN is vaild for %s, this NG version is (%s)" % major_version))

    ## check function 2
    status,_info,error = check_memory_allocation(loglines)
    info.append(''.join(_info))
    result.update(status=status,info=info,error=error)
    return result