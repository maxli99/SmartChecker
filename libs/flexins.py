import re
from tools import read_cmdblock_from_log
from networkelement import NetworkElement

__version__ = "v0.5"

command_end_mark = "COMMAND EXECUTED"

class FlexiNS(NetworkElement):
    """Class parse and stroe basic infomation of FlexiNS
example:
    ns = FlexiNS()
    ns.parse_log("log/nsinfo.log")

    print ns.version    
    """

    def parse_log(self,logfile):
        loglines = file(logfile).readlines()
        self._data['version'] = _get_ns_version(loglines)

    def match_version(self,versions):
        nsversion = self.version.get('BU','')
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
 
    
def _get_ns_version(loglines):
    """This function will parse the FlexiNS version info from log lines.
parameters:
    loglines   log lines
return:
    return  a dict include package's status and id info or an empty dict.
    
    example: {'BU': 'N5 1.17-5', 'FB': 'N5 1.17-5', 'NW': 'N4 1.19-2', 'UT': 'N4 1.19-2'}
    
    """
    pkgid_pat = re.compile("\s+(BU|FB|NW)\s+.*?\n\s+(\w\d [\d\.-]+)")

    logtxt = read_cmdblock_from_log(loglines,'WQO:CR;',command_end_mark)
    version = dict(pkgid_pat.findall(logtxt))
    
    return version


def get_ns_version(configlog):
	"""This function will parse the NS version info from logfile.
	Input  logfile
	return  a tuple include (ns_version)
	example: ('N5 1.19-3', 'N5 1.17-5','UNKNOWN')
	"""
	version = None
	#search the version info , the real version as default is mark with 'Y' in 'DEF' column
	version_pat = re.compile(r"ZWQO.*?      Y    Y",re.S)

	try:	
		log = ''.join(file(configlog).readlines())
        
		r=version_pat.search(log)
		if r:
			logpos=r.end()
			#version info is the line between pos:30--43
			version = log[logpos+30:logpos+43]
			
		return version
				
	except IOError,e:
		print("IOError: %s" % e)
		return 'UNKNOWN'
		
if __name__ == "__main__":
	nsversion = get_ns_version('..\\log\\test_ALL_NS_TN_check.log')
	print nsversion
