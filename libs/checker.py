# -*- coding: utf-8 -*-
import os,yaml,re,json
from subprocess import check_output, STDOUT,PIPE,CalledProcessError
from collections import Counter
from importlib import import_module
from libs.tools import to_unicode

__version__ = "v1.0"
MODULE_PATH = 'modules'
IGNORE_FILES = ['^_', '^\.', '\.pyc$']
_filefilters = [re.compile(pat) for pat in IGNORE_FILES]

###############################################################
# Common Functions
###############################################################
def dict2csv(dictdata,columnnames):
    """Transfer the dict data to csv string.
    """
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

###############################################################
# Class CheckStatus
###############################################################
class CheckModuleError(Exception):
    pass
class BasicInfoMissing(CheckModuleError):
    pass
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

###############################################################
# Class ShellModule
###############################################################
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

class CheckList(object):
    """Class store and handle the data of check list.
    checklist = Checklist(checklist_file)
    checklist.module
    """
    def __init__(self,filename=''):
        self.info = {}
        self.modules = []
        self.filename = os.path.split(filename)[1]
        if filename:
            self.load(filename)

    @property
    def name(self):
        if self.filename:
            return self.filename[:-4]
        else:
            return ""

    @property
    def templates(self):
        return self.info.get('templates',{})
    @property
    def netype(self):
        return self.info.get('netype','UNKNOWN')
    
    @property
    def paths(self):
        return self.info.get('paths',{})
    @property
    def modules_name(self):
        return self.info.get('modules_name',[])

    def load(self,filename):
        self.info.update(yaml.load(file(filename)))

    def getinfo(self,key):
        return self.info.get(key)

    def import_modules(self,modules_filename=None):
        if modules_filename:
            self._modules_name = modules_filename
        module_path = self.info['paths']['modules']
        module_names = filter(ignore_files,self.info['modules_name'])
        self.modules = ImportCheckModules(self)

        return self.modules
    def __repr__(self):
        return "CheckList(%(filename)s)" % self.__dict__
def ImportCheckModules(checklist):
    """Import the modules and return the modules list.
    """
    modules = []
    modulefilenames = filter(ignore_files,checklist.modules_name)
    modulepath = checklist.paths['modules']

    for name in modulefilenames:
        #print 'module path/name: %s\\%s' % (path,name)
        if name.endswith('.py'):
            mpath = '.'.join(os.path.split(modulepath))
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


class ResultInfo(object):
    """Storing the information of the check result.

    status,  PASSED/FAILED/UNKNOW/
    info,    information.
    error,   error information.
    """
    strformat = " Status: %(status)s\n   Info:\n%(info)s\n  error:%(error)s"
    keys = ['status','info','error']
    def __init__(self,name,priority=''):
        self.name = name
        self.criteria = ''
        self.priority = priority
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
        self.data['info'] = value if isinstance(value, unicode) else unicode(value, "utf-8")

    @property
    def error(self):
        return self.data['error']

    @error.setter
    def error(self,value):
        self.data['error'] = value if isinstance(value, unicode) else unicode(value, "utf-8")

    def _encode_to_unicode(self):
        for index in xrange(len(self.data['info'])):
            self.data['info'][index] = self.data['info'][index] \
                if isinstance(self.data['info'][index], unicode) \
                else unicode(self.data['info'][index], "utf-8")
        self.data['error'] = self.data['error'] if isinstance(self.data['error'], unicode) else unicode(self.data['error'], "utf-8")

    def update(self,**kwargs):
        self.data.update(kwargs)
        self._encode_to_unicode()

    def load(self,**kwargs):
        "obslated function, please use the update instead."
        self.update(**kwargs)
        self._encode_to_unicode()

    def dump(self,oformat='reading'):
        if oformat == 'reading':
            data = self.data.copy()
            #data['info'] = "\n".join(data['info'])
            data['info'] = "\n".join(data['info'])
            return ResultInfo.strformat % data

        elif oformat == 'json':
            return json.dumps(self.data)
        elif oformat == 'csv':
            return dict2csv(self.data, ResultInfo.keys)
        else:
            #status_str = "\n[%s] %s, " % (idx+1,m.name)
            return ResultInfo.strformat  % self.data

    def dumpstr(self,template=None):
        """
        """
        strbuf = []


class ResultList(object):
    """this class store all the check results.
    """
    def __init__(self,hostname=''):
        self._results = []
        self.hostname = hostname
        self.report_filename = ''
        self.template_type = ''

    def append(self,obj):
        self._results.append(obj)

    def __len__(self):
        return len(self._results)

    def stats(self):
        return Counter([r.data['status'] for r in self._results])

    def stats_dict(self):
        status = {}
        for k, v in Counter([r.data['status'] for r in self._results]).items():
            status[k] = v
        return status

    def __iter__(self):
        return iter(self._results)
