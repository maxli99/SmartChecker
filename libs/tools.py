# -*- coding: utf-8 -*-
import codecs

def to_unicode(line):
    """translate the string line to unicode.
    """
    if isinstance(line,unicode):
        return line
    else:
        return line.decode('utf-8')

class MessageBuffer(object):
    """Class for store the information for sending to differnt destination later.
    """
    def __init__(self,lineformat="%s",size=1024*1024,template=None):
        self.buffer = []
        self.size = size
        self.lineformat = lineformat
        self.template = template

    def append(self,txt):
        self.buffer.append(self.lineformat % txt)


    def to_console(self, concatenation="\n"):
        _lines = map(to_unicode,self.buffer)
        utextblock = concatenation.join(_lines)
        #print utextblock
        if self.template:
            print(template % utextblock)
        else:
            print(utextblock)

    def to_file(self,filename):
        with codecs.open(filename,'wb','utf-8') as fp:
            fp.writelines(self.buffer)

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