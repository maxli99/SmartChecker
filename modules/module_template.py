"""Check if memory leaks in AS/SAB nodes

"""
import re
from libcheck import CheckStatus,ResultInfo,ModuleBase

## Optional variables
target_version = 3.2    
pat_memfail = re.compile("shm_gwup_proxy.gwup.sa.sa_rule.filter.interr.mem_alloc_failed_for_linear_filters = (\d+)")
pat_memallo = re.compile("info ([\w\d-]+) featuremem.*FASTPATH_MALLOC dynamic allocated bytes \[chunks\]: (\d+)/(\d+)")

class CheckMemoryLeak(ModuleBase):
    def __init__(self):
        module_id = 'NG20150518.01'
        name      = "memory_leak"
        desc      = __doc__
        tags      = ['flexing','china']
        priority  = 'critical'
        mem_threshold = {'AS':110,'SAB':500}  #MB
        criteria      = "memory usage: AS < %(AS)sMB or SAB < %(SAB)sMB" % mem_threshold


##--------------------------------------------
## Mandatory function: run
##--------------------------------------------        
def run(logfile):
    "this function execute the check steps and return "
    loglines = file(logfile).readlines()
    result = ResultInfo(name)
    info = []
    error = ''
    _checked = False
    
    _mem = {'AS':[],'SAB':[]}
    for line in loglines:
        r1 = pat_memfail.search(line)
        if r1:
            result.status = CheckStatus.FAILED
        
        r2 = pat_memallo.search(line)
        if r2:
            mem = int(r2.groups()[1])/1024.0/1024.0
            node = r2.groups()[0]
            node_type = re.sub('[\d+-]','',node)
            _mem[node_type].append((node,mem))
            _checked = True
            if mem > mem_threshold[node_type]:
                result.status = CheckStatus.FAILED
                info.append('%s memory is closing to full: %.5s MB' %(node, mem))
               
    if result.status !=CheckStatus.FAILED:
        for ntype,memlist in _mem.items():
            if len(memlist) == 0: continue
            maxmem=sorted(memlist,key=lambda x:x[1],reverse=True)[0]
            info.append('%s has a max memory %.6s MB' % maxmem)
    print "status/checked:",result.status,_checked
    if result.status==CheckStatus.UNKNOWN and _checked:
        result.status = CheckStatus.PASSED

    result.load(info=info,error=error)
    return result