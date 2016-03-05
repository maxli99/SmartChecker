import os,yaml,re,json
from subprocess import check_output, STDOUT,PIPE,CalledProcessError    
from collections import Counter
from importlib import import_module

MODULE_PATH = 'modules'
IGNORE_FILES = ['^_', '^\.', '\.pyc$']
_filefilters = [re.compile(pat) for pat in IGNORE_FILES]

class CheckStatus(object):
    PASSED = 'PASSED'      # check result is passed
    FAILED = 'FAILED'      # check result is failed
    UNKNOWN = 'UNKNOWN'    # unknown stituation
    RUNERR  = 'RUNERR'     # error in runtime 
    UNCHECKED = 'UNCHECKED'

def validateResult(result):
    if hasattr(CheckStatus,result.upper):
        return result.upper()
    return UNKNOWN

class ShellModule(object):
    """This class wrap the non-python script.
    """
    def __init__(self,scriptname, path, *args, **kwargs):
        self.name = scriptname
        self.desc = 'shell script'  # read from the script
        self.args = args
        self.criteria = "criteria to determinate the check"
        self.kwargs = kwargs

        self.path = path

    def run(self,parameters):
        result = ResultInfo(self.name)

        cmd = "%(cmd)s %(parameter)s" % dict(cmd=self.name,parameter=parameters)
        cmdline = "\\".join([self.path,cmd])  ### only for WINDOWS

        try:
            out = check_output(cmdline,shell=True,stderr=PIPE)
            result.data.update(json.loads(out.strip().split('\n')[-1]))
            #print 'result status:',result.data['status']
        ## if return code is non-zero. error happens.
        except CalledProcessError,err:
            error = "  errmsg: <<%s>> " % err
            result.load(status=CheckStatus.RUNERR,error=error)

        #result = validateResult(result)  
        return result

def dict2csv(dictdata,columnnames):
    values =[]
    for name in columnnames:
        if isinstance(dictdata[name],list):
            values.append('|'.join(dictdata[name]))
        else:
            values.append(str(dictdata[name]))

    return ','.join(values)

def ignore_files(filename):
    """filter the non-script filenames
    if '.ignore_file' is found in 'modules' directory, then those filter in file 
    will be added to the patterns
    """
    for pat in _filefilters:
        if pat.search(filename):
            return False
    return True

def ImportCheckModules(moduleslist, path=MODULE_PATH):

    if moduleslist:     
        #read the script filename from file which specified in command parameter "-m".
        modules_info = yaml.load(file(moduleslist))
        path = modules_info.get('path',MODULE_PATH)
        #print "path,mname:",path,modules_info.get('modules')
        modulefilenames = filter(ignore_files,modules_info.get('modules',None))
        #print "modulefilenames:",modulefilenames
    else:
        # read the script filename from the modules directory.
        modulefilenames = filter(ignore_files, os.listdir(path))
        #print modulefilenames
    modules = []
    for name in modulefilenames:
        #print 'module path/name: %s\\%s' % (path,name)
        if name.endswith('.py'):
            mpath = '.'.join(os.path.split(path))
            mname = '.'.join([mpath,name[:-3]])
            #print "mname:",mpath,name[:-3]
            modules.append(import_module(mname))
        elif os.path.isdir(os.path.join(path,name)):
            # this name is a directory.
            continue
        else:
            # non-python script modules
            #print "name:",name
            modules.append(ShellModule(name,path))

    return modules

class ModuleBase(object):
    """Base class for check module
    """

    def __init__(self,name=''):
        self.name = name
        cmdset = []

    def run(self):
        """the check action should be done here.
        """
        print "I'm checking the log"
        
    def log_commands(self):
        """output the commands which used to collect log.
        """
        return '\n'.join(self.cmdset)
            

class ResultInfo(object):
    """Storing the information of the check result.

    status,  PASSED/FAILED/UNKNOW/
    info,    information.
    error,   error information.
    """
    strformat = " Status: %(status)s\n   Info: %(info)s\n  error:%(error)s"
    keys = ['status','info','error']
    def __init__(self,name):
        self.name = name
        self.data = {'status' : CheckStatus.UNKNOWN,
                      'info'   : '',
                      'error'  : '',
                    }
        

    def setvalue(self,key,value):
        if key not in ResultInfo.keys:
            return False
        self.__dict__[key] == value
        return True

    @property    
    def status(self):
        return self.data['status']
    @status.setter
    def status(self,value):
        self.data['status'] = value

    @property
    def info(self):
        return self.data['info']

    @info.setter
    def info(self,value):
        self.data['info'] = value
    
    @property
    def error(self):
        return self.data['error']

    @error.setter
    def error(self,value):
        self.data['error']
    
    def load(self,**kwargs):
        self.data.update(kwargs)

    def dump(self,oformat='reading'):
        if oformat == 'reading':
            data = self.data.copy()
            data['info'] = "\n".join(data['info'])
            print ResultInfo.strformat % data

        elif oformat == 'json':
            print json.dumps(self.data)
        elif oformat == 'csv':
            print dict2csv(self.data, ResultInfo.keys)
        else:
            #status_str = "\n[%s] %s, " % (idx+1,m.name)
            print ResultInfo.strformat  % self.dat       


class ResultList(object):
	"""this class store all the check results.
	"""
	def __init__(self):
		self._results = []

	def append(self,obj):
		self._results.append(obj)

	def __len__(self):
		return len(self._results)

	def stats(self):
		return Counter([r.data['status'] for r in self._results])
