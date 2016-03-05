"""Check the NTP setting for the 2015 leap second issue
In case of systems having AMPP1 -A blades, a critical bug was found in kernel that may cause
a deadlock to occur when NTP leap second is applied to the system. If the fault should occur
the system will restart itself (via watchdog functionality) thus causing a service break.
"""
import re
from libs.checker import ResultInfo,CheckStatus

## Mandatory variables
##--------------------------------------------
module_id = '20150518.01'
tag  = ['flexing','china']
priority = 'critical'
name = "ntp setting check for leap second issue"
desc = __doc__
criteria = "NTP status is (unlocked,enabled)"
result = ResultInfo(name)
error = ''
##--------------------------------------------

##--------------------------------------------

##--------------------------------------------
## Optional variables
target_version = 3.2
pats_ntp = {'cluster': re.compile(r"ClusterNTP:\nadministrative\((\w+)\)\noperational\((\w+)\)"),
        'node'   : re.compile(r"NodeNTP:\nadministrative\((\w+)\)\noperational\((\w+)\)"),
       }
ntpstatus_str = "ClusterNTP:%(cluster)s,NodeNTP: %(node)s"
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
    cmds = ['fshascli -s /ClusterNTP',
            'fshascli -s /NodeNTP',
            ]
    for cmd in cmds:
        print cmd

##--------------------------------------------
## Mandatory function: run
##--------------------------------------------
def run(logfile):
    logtxt = read_block(logfile,'ntp_stat')

    ntpstatus={name:'' for name in pats_ntp}
    status = CheckStatus.UNCHECKED

    for name,pat in pats_ntp.items():
        r=pat.search(logtxt)
        if r:
            ntpstatus[name] = r.groups()
            if r.groups()[0] == 'UNLOCKED':
                status = CheckStatus.FAILED

    #print ntpstatus_str, ntpstatus
    if status == CheckStatus.UNCHECKED:
        status = CheckStatus.UNKNOWN
    result.load(status=status,info=[ntpstatus_str % ntpstatus],error=error)

    return result
