import re
from hwparser import HardwareInfo
from networkelement import NetworkElement

version_names = ('major','release','hardware')

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

    def match_version(self,major=[],release=[],hardware=[]):
        """match_version(major=['3.2'], release=['r23456'])

        return (marjor_flag,release_flag,hardware_flag)
        """
        match_flag  = {'major':False, 'release':False, 'hardware':False}
        
        for ver in major:
            if re.match(ver,self.version['major']):
                match_flag['major'] = True
                break
        for ver in release:
            if re.match(ver,self.version['release']):
                match_flag['release'] = True
                break
        for ver in hardware:
            if re.match(ver,self.version['hardware']):
                match_flag['hardware'] = True
                break

        return match_flag

    def __repr__(self):
        return "FlexiNSObj:<%(hostname)s, %(version)s>" % self._data


    
def _get_ng_version(loglines):
    """This function will parse the NG version info from logfile.
parameters:
    loglines    config log lines
return:
    return  a tuple include (major_version, release_version, hardware_version)
    
    example: {'major': 3.2', 'release': '123445', 'hardware':'2'}
    
    """
    version = None
    version_pat = re.compile("_NG([\d\._]+)_r(\d+)_AB(\d+)")
    
    if not loglines:
        return None

    log = ''.join(loglines)
    check = version_pat.search(log)

    if check:
        version = dict(zip(version_names,check.groups()))
    
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
