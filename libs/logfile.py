# -*- coding: utf-8 -*-

__version__ = '0.5'
__author__  = 'jun1.liu@nokia.com'

import os
import re
from collections import defaultdict

LOGFILE_POSTFIX = ['.log','.txt']

log_patterns = {'FlexiNG' : re.compile("fsclish"),
                'FlexiNS' : re.compile("COMMAND EXECUTED")}

class LogFileError(Exception):
    pass

def istextfile(filename):
    for postfix in LOGFILE_POSTFIX:
        if filename.endswith(postfix):
            return True
    return False

class LogFile:
    """Handling the logfile for analysis
    """

    def __init__(self,filename):
        _path,_name = os.path.split(filename)
        self.path = _path
        self.filename = None

        _postfix = filename.split('.')[-1]
        if filename and istextfile(filename):
            self.fp = file(filename)
            self.filename = _name            
        else:
            self.fp = None

    @property   
    def state(self):
        return bool(self.fp)

    def loglines(self):
        return self.fp.readlines()

    def match(self,netype):
        """return True if the log type match the netype.
        """
        for line in self.loglines():
            if log_patterns[netype].search(line):
                return True
        return False

    def __repr__(self):
        return "LogFile(%s)" % self.filename
