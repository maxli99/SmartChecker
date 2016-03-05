"""Module for handling Hardware data
"""
class HardwareInfo(object):
    """class read and store hardware info of FlexiNG
    """
    def __init__(self,logfile=None):
        if logfile:
            self.loaddata(logfile)
        self.info = {}

    def parse_log(self,logfile):
        pass
    def get(self,attr):
        return self.info.get(attr,None)

