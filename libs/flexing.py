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

        _hostver = _get_ng_hostname_version(loglines)
        self._load_data(_hostver)
        ##extract the hostnme

    def match_version(self,major=None,release=None,hardware=None):
        """ Check if the element's versio match the specified version number.

        >>> match_version(major=['3.2'], release=['r23456'])  #match major and release
        >>> ng.match_version(major=['3.2'])     #only match the major.

        return {'major':True, 'release':False, 'hardware':False}
        """
        match_flag  = {'major':False, 'release':False, 'hardware':False}
        major = major or []
        release = release or []
        hardware = hardware or []
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
        try:
            _hwver = self._data['version'].get('hardware','?')
        except Exception as e:
            _hwver = '?'
        _data = self._data.copy()
        _data['hardware'] = "AB%s" % _hwver
        return "FlexiNG(%(hostname)s, HW=%(hardware)s)" % _data

def _get_ng_version(loglines):
    """This function will parse the NG version info from logfile.
    parameters:
        loglines    config log lines
    return:
        return  a tuple include (major_version, release_version, hardware_version)
        
        example: {'major': 3.2', 'release': '123445', 'hardware':'2'}
    
    """
    version = None
    version_pat = re.compile("_NG([\w\d\._]+)_r(\d+)_AB(\d+)")
    
    if not loglines:
        return None

    log = ''.join(loglines)
    check = version_pat.search(log)

    if check:
        version = dict(zip(version_names,check.groups()))

    return version

def _get_ng_hostname_version(loglines):
    names = ['hostname','version']
    pat_host = re.compile("fsLogicalNetworkElemId: (\w+)")
    pat_version = re.compile("fsStaticDataDelivery: R_NG([\w\d\._]+)_r(\d+)_AB(\d+)")

    h_flag=v_flag=False
    hostname = ''
    version = {}
    for line in loglines:
        r1 = pat_host.search(line)
        r2 = pat_version.search(line)
        if r1:
            hostname = r1.groups()[0]
            h_flag = True
        if r2:
            version = dict(zip(version_names,r2.groups()))
            v_flag = True

        if h_flag and v_flag:
            break      
    return dict(zip(names,(hostname,version)))


## phaseout this function at 3/28
# def get_ng_version(configlog):
#     """This function will parse the NG version info from logfile.
#     Input    config logfile
#     return  a tuple include (major_version, release_version, hardware_version)
#     example: ('3.2', '123445', '2')
#     """
#     version = None
#     version_pat = re.compile("_NG([\d\._]+)_r(\d+)_AB(\d+)")

#     try:
#         log = ''.join(file(configlog).readlines())
#     except IOError,e:
#         print("IOError: %s" % e)
#         exit(1)
#     check = version_pat.search(log)

#     if check:
#         version = check.groups()
#     return version

def get_hw_info(configlog):
    hwinfo = HardwareInfo()
    return hwinfo

