# -*- coding: utf-8 -*-

__version__ = '0.6'
__author__  = 'jun1.liu@nokia.com'

class NetworkElement(object):
    """Abstract Class parse and stroe basic infomation of network Element   
    """
    def __init__(self,hostname='',logfile=None):
        self.logfile = logfile
        self._data = {}
        self._data['hostname'] = hostname
        if logfile:
            self.parse_log(logfile)

    def parse_log(self,logfile):
        """parse the log and extract the info save to self._data.
        """
        pass

    def _load_data(self, namelist, data):
        """load the needed data from the data dict
        """
        for name in namelist:
            if name in data:
                self._data[name] = data[name]


    def get(self,key):
        return self._data.get(key,None)

    def match_version(self,versions):
        """check if the element's version match the given 'versions'.
the version could be a list include multi version id. or a string of version id.
        """
        pass

    def __repr__(self):
        return "NetworkElementObj:<%s>" % self.hostname

    @property
    def hostname(self):
        return self._data['hostname']

    @property
    def version(self):
        return self._data['version']

def extract_data(datainfo,loglines):
    """return a dict include the data extract from the loglines.
Arguments:
    datainfo        a dict contains the data names,command and the patterns
    command
                    {'names':['BU','FB','NW','UT'],
                     'command': 'ZCWQ'
                     'pattern': re.compile("xxxx"),
                     'match_method': 'findall'
Return:
    a dict include the data with name.
    """
    logtxt = read_cmdblock_from_log(loglines,datainfo['command'])

    names = datainfo['names']
    method = datainfo['match_method']
    pat = datainfo['pattern']

    if method == 'search':
        r = pat.search(logtxt)
        if r:
            _data = r.groups()
        else:
            return None    
    elif method == 'findall':
        r = pat.findall(logtxt)
        if r:
            _data = r
        else:
            return None

    return dict(zip(names,_data))        