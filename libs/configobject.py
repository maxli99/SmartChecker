### Another config file handling. the file name could be arbitrary.
class ConfigObject(object):
    """usage: 
        conf = ConfigObject('alarm.conf')
        conf = ConfigObject(dict)
        
        #get the config values:
        conf.oss_trap_ip
        conf.get('oss_trap_ip')
        
    """
    def __init__(self,parameters=None):
        """parameters can be a filename or a dict include parameters.
        """
        if isinstance(parameters,str):
            self.read(parameters)
        elif isinstance(parameters,dict):
            self.update(parameters)
    
    def read(self,confile):
        try:
            execfile(confile,globals(),self.__dict__)
        except IOError,e:
            print "Config File not found:%s" % e
            exit(1)
    def update(self,dictpara):
        self.__dict__.update(dictpara)

    def getall(self):
        """return a dict include all configuration"""
        return self.__dict__
    
    def items(self):
        return self.__dict__.items()
        
    def set(self,key,value):
        self.__dict__[key] = value
        
    def get(self,key,notfound=None):
        """return the value for 'key' or notfound if key not exist"""
        return self.__dict__.get(key,notfound)
    def __repr__(self):
        import pprint
        return pprint.pformat(self.__dict__)
        
#### or 
#conf = {} or class conf:pass
#execfile('file.conf',globals(),conf)
#conf[xxx]  