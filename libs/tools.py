# -*- coding: utf-8 -*-
import sys,codecs

def to_unicode(line):
    """translate the string line to unicode.
    """
    if isinstance(line,unicode):
        return line
    else:
        return line.decode('utf-8')

class InfoCache(object):
    """A singleton Class can store the information shared in global/modules.
    """
    _cache = {}

    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._cache
        return self

    def set(self,key,value):
        self._cache[key] = value   
        return self._cache[key]
        
    def get(self,key):
        return self._cache.get(key,None)
        
    def __repr__(self):
        return "InfoCache:%s" % self._cache
    
    def __contains__(self,key):
        return key in self._cache
        
class MessageBuffer(object):
    """Store the information for sending to differnt destination later.
    """
    def __init__(self,lineformat="%s",size=1024*1024,template=None):
        self.buffer = []
        self.size = size
        self.lineformat = lineformat
        self.template = template    #template for message.

    def append(self,txt):
        self.buffer.append(self.lineformat % txt)


    def to_console(self, concatenation="\n"):
        _lines = map(to_unicode,self.buffer)
        utextblock = concatenation.join(_lines)


        if self.template:
            print(template % utextblock)
        else:
            #print("typeof:utextblock",type(utextblock),"sysencoding:",sys.stdout.encoding)
            #unicode, cp936/utf-8
            sys.stdout.write(utextblock)

    def to_file(self,filename):
        _lines = map(to_unicode,self.buffer)
        with codecs.open(filename,'wb','utf-8') as fp:
            fp.writelines(_lines)

    def to_socket(self):
        pass

    def output(self,mode='console',filename=None):
        if mode == "console":
            self.to_console()
        elif mode in ["server",'gui']:
            self.to_socket()
        elif mode == "file":
            self.to_file(filename)

def read_cmdblock_from_log(logfile,startline=None,endline=None):
    """read the command block from logfile.

    parameters:
        startline,  string
        endline,    string

    return:
        the text block of the command if command was found or
        an empty string('')  if command was not found.

    """
    blocklines = [] 
    flag_start = False
    loglines = file(logfile).readlines()

    for line in loglines:
        if flag_start:
            blocklines.append(line)
            if endline in line:
                break
        elif startline in line:
            flag_start = True
            blocklines.append(line)
            #print "start line found!"

    return ''.join(blocklines)            