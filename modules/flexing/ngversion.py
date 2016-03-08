# -*- coding: utf-8 -*-
"""FlexiNG Version Checking
  Check the NG version, passed if version >= 3.1
"""
import re
from libs.flexing import get_ng_version
from libs.checker import ResultInfo,CheckStatus

## Mandatory variables 
##-----------------------------------------------------
check_id = '20150101.01'
tags = ['flexing','minor']
name = "ngversion"
desc = __doc__
criteria = "Check if version number in ['3.1_1.0','3.2']"
##-----------------------------------------------------

## Optional variables
##-----------------------------------------------------
# available target versions:
target_versions = ['3.1_1.0','3.2']
##-----------------------------------------------------

    
## Mandatory function: run
def run(logfile):
    result = ResultInfo(name)
    info   = []
    errmsg = ''
    
    version = get_ng_version(logfile)
    #version(version,release,hw_ver) -> ('3.1_1.0', '235397', '2')

    if version and version[0] in target_versions:
        result.status = CheckStatus.PASSED
        info.append("    - NG%s_r%s_AB%s" % version)
    elif version and version[0] not in target_versions:
        result.status = CheckStatus.FAILED
        info.append("    - NG%s_r%s_AB%s" % version)
    else:
        result.status = CheckStatus.UNKNOWN
    
    result.update(info=info,error=errmsg)
    return result