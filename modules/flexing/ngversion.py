# -*- coding: utf-8 -*-
"""FlexiNG Version Checking
  Check the NG version, passed if version >= 3.1
"""
import re
#from libs.flexing import get_ng_version
from libs.checker import ResultInfo,CheckStatus
from libs.infocache import InfoCache
from libs.tools import debugmsg

## Mandatory variables 
##-----------------------------------------------------
check_id = 'ngbase.20150101.01'
tags = ['flexing','minor']
name = "ngversion"
desc = __doc__
criteria = "Check if version number in ['3.1_1.0','3.2']"
##-----------------------------------------------------

## Optional variables
##-----------------------------------------------------
# available target versions:
target_versions = ['3.1_1.0','3.2']
check_commands = []
shareinfo = InfoCache()

##-----------------------------------------------------

    
## Mandatory function: run
def run(logfile):
    result = ResultInfo(name)
    info   = []
    errmsg = ''
    
    ng = shareinfo.get('FlexiNG')
    #version(version,release,hw_ver) -> ('3.1_1.0', '235397', 'AB2')
    debugmsg(ng)
    if ng and ng.get('version'):
        match=ng.match_version(major=target_versions)
        if match['major']:
            result.status = CheckStatus.PASSED
        else:
            result.status = CheckStatus.FAILED
        info.append("FlexiNG version checked: %s" % str(ng.version))
    else:
        status = CheckStatus.UNKNOWN
        info.append("unknow version")
        error = " - Can't find the packages info from log."
    
    result.update(info=info,error=errmsg)
    return result