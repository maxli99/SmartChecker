import re
from hwparser import HardwareInfo
from networkelement import NetworkElement

class FlexiNG(NetworkElement):
    """Class parse and stroe basic infomation of FlexiNG
example:
    ns = FlexiNG()
    ns.parse_log("log/nginfo.log")

    print ng.version    
    """

    def parse_log(self,logfile):
        loglines = file(logfile).readlines()
        self._data['version'] = _get_ng_version(loglines)

    def match_version(self,major=None,release=None,hardware=None):

        if isinstance(versions,list):
            for ver in versions:
                if re.match(ver,nsversion):
                    return True
        else:
            if re.match(versions,nsversion):
                return True
        return False

    def __repr__(self):
        return "FlexiNSObj:<%s>" % self.hostname    


    
def _get_ng_version(loglines):
    """This function will parse the NG version info from logfile.
parameters:
    loglines    config log lines
return:
    return  a tuple include (major_version, release_version, hardware_version)
    
    example: ('3.2', '123445', '2')
    
    """
    version = None
    version_pat = re.compile("_NG([\d\._]+)_r(\d+)_AB(\d+)")
    if not loglines:
        return None

    log = ''.join(loglines)
    check = version_pat.search(log)

    if check:
        version = check.groups()
    return version

def get_ng_version(configlog):
    """This function will parse the NG version info from logfile.
    Input    config logfile
    return  a tuple include (major_version, release_version, hardware_version)
    example: ('3.2', '123445', '2')
    """
    version = None
    version_pat = re.compile("_NG([\d\._]+)_r(\d+)_AB(\d+)")

    try:
        log = ''.join(file(configlog).readlines())
    except IOError,e:
        print("IOError: %s" % e)
        exit(1)
    check = version_pat.search(log)

    if check:
        version = check.groups()
    return version
    
def get_hw_info(configlog):
    hwinfo = HardwareInfo()
    return hwinfo

if __name__ == "__main__":
    hw = get_hw_info('fake')
    print hw
