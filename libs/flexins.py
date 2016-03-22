import re
from libs.tools import read_cmdblock_from_log

command_end_mark = "COMMAND EXECUTED"

class FlexiNS(object):
    """
    """
    def __init__(self,logfile=None):
        self.logfile = logfile
        self._data = {}

        if logfile:
            self.parse_log(logfile)

    def parse_log(self,logfile):
        loglines = file(logfile).readlines()
        self._data['hostname'] = 'DummyHost'
        self._data['version'] = get_ns_version(loglines)

    def get(self,key):
        return self._data.get(key,None)

    def match_version(self,versionlist):
        for ver in versionlist:
            if re.match(ver,self.version):
                return True
        return False
        
    def __repr__(self):
        return "FlexiNSObj:<%s>" % self.hostname

    @property
    def hostname(self):
        return self._data['hostname']

    @property
    def version(self):
        return self._data['version']
    
    
def get_ns_version(loglines):
    """This function will parse the FlexiNS version info from logfile.
parameters:
    configlog    config logfiler
return:
    return  a dict include package's status and id info.
    
    example: {'BU': 'N5 1.17-5', 'FB': 'N5 1.17-5', 'NW': 'N4 1.19-2', 'UT': 'N4 1.19-2'}
    
    """
    pkgid_pat = re.compile("\s+(BU|FB|NW)\s+.*?\n\s+(\w\d [\d\.-]+)")

    logtxt = read_cmdblock_from_log(loglines,'WQO:CR;',command_end_mark)
    version = dict(pkgid_pat.findall(logtxt))
    
    return version



