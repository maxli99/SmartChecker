class CheckStatus(object):
    PASSED = 'PASSED'      # check result is passed
    FAILED = 'FAILED'      # check result is failed
    UNKNOWN = 'UNKNOWN'    # unknown stituation
    RUNERR  = 'RUNERR'     # error in runtime
    UNCHECKED = 'UNCHECKED'
    
    VERSION_UNKNOWN = -1
    VERSION_MATCHED = 1
    VERSION_UNMATCHED = 0
    
    def allstatus(self):
        pass
        
    def __getattr__(self,key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return None
    