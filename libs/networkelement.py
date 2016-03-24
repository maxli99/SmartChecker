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