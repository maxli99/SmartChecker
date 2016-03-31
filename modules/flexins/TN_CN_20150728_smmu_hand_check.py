# -*- coding: utf-8 -*-
__author__='liming.wang'
__date__='20160308'
u''' SPMU GNRPRB hand checking
Case 描述：当MME/SGSN运行大约248天后，SMMU的GRNPRB的hand group 2里面的50个hand会自动被
释放，而不能重启创建，从现象上可以观察到终端用户PDP激活困难，SGSN会出大量的
0x167( no_rsp_co_process_c )的错误代码
临时解决方案：重启所有的 SMMU 单元
'''
import re
from libs.checker import ResultInfo,CheckStatus
from libs.log_spliter import LogSpliter, LOG_TYPE_FLEXI_NS

## Mandatory variables
##--------------------------------------------
module_id = 'fns2016030720'
tag  = ['flexing','china']
priority = 'critical'
name = "SMMU GRNPRB hand checking"
desc = __doc__
criteria = u''' 检查SMMU GRNPRB hand group 2 的hand数，50为通过
'''
result = ResultInfo(name,priority=priority)
#error = ''
##--------------------------------------------

##--------------------------------------------

##--------------------------------------------
## Optional variables
target_version = ['NS30', 'NS40', 'NS15']
check_commands= [('ZDDE:SMMU,x:"ZL:9","ZLP:9,FAM","Z9H:404";','Show GRNPRB hand state,x is the unit id of SMMU.')]
#match_start= 'HAND FO:PREV NEXT TIME     GR STATE    STABITS  JBUFFER      RCOMP FAM  PROC FO'
patten = re.compile("^[0-9,A-F]{4} [0-9,A-F]{2} [0-9,A-F]{4}")
smmu_info="SMMU-%s GRNPRB hand check %s\n"
##

def read_block(logfile,blkname):
    # loglines = file(logfile).readlines()
    #
    # return ''.join(loglines)
    logspliter=LogSpliter(type=LOG_TYPE_FLEXI_NS)
    logspliter.load(logfile)
    return logspliter.get_log(blkname,fuzzy=True)

##--------------------------------------------
## Mandatory function: log_collection
##--------------------------------------------
def log_collection():
    cmds = ['ZDDE:SMMU,x:"ZL:9","ZLP:9,FAM","Z9H:132";'
            ]
    for cmd in cmds:
        print cmd

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------
def run(logfile):
    rsult_info=[]
    total_status=CheckStatus.UNKNOWN


    blocks = read_block(logfile,'ZDDE:SMMU,')

    for block in blocks:
        m=re.match(r".+SMMU,(\d+)",block.command)
        unit_index=''
        if m:
            unit_index=m.groups(1)[0]
        else:
            continue
        status = CheckStatus.UNCHECKED
        hands=[]
        for line in list(block.result):
            line=line.strip()
            if (patten.search(line)):
                fields=line.split(' ')
                if fields[5]=='02':
                    hands.append(line[:4])
        if len(hands)==50:
            status=CheckStatus.PASSED
            total_status=CheckStatus.PASSED
        else:
            status=CheckStatus.FAILED
            total_status=CheckStatus.FAILED

        if status == CheckStatus.UNCHECKED:
            status = CheckStatus.UNKNOWN
        rsult_info.append(smmu_info %(unit_index,status))
    if total_status==CheckStatus.UNKNOWN:
        error = "Can't find hand status in this log!"
    else:
        error =''

    result.update(status=total_status,info=rsult_info,error=error)

    return result
