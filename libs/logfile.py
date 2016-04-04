# -*- coding: utf-8 -*-

__version__ = '0.5'
__author__  = 'jun1.liu@nokia.com'

import os
import re
from collections import defaultdict

log_patterns = {'FlexiNG' : re.compile("fsclish"),
                'FlexiNS' : re.compile("COMMAND EXECUTED")}

class LogFile:
    """Handling the logfile for analysis
    """
    def __init__(self,filename=''):
        _path,_name = os.path.split(filename)
        self.path = _path
        self.filename = _name

        if filename:
            self.fp = file(filename)

    def loglines(self):
        return self.fp.readlines()

    def match(self,netype):
        """return True if the log type match the netype.
        """
        for line in self.loglines():
            if log_patterns[netype].search(line):
                return True
        return False


