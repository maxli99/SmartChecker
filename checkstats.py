#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Smartchecker Statitstics Report
this tool read the smartchecker log and caculate the stats of the results.
the log file is defined in `checker.conf` or `log/smartchecker.log` by
default.

checkstats.py  <start_date>,[end_date]

example:
     #caculate all the log from 2016-05-16 and before 2016-05-17(not include)
     checkstats.py 2016-05-16,2016-05-17

     #caculate all the log from 2016-05-16 to now
     checkstats.py 2016-05-16
"""
import re,sys
from libs.configobject import ConfigObject

conf = ConfigObject('checker.conf')
stats_pat = re.compile("Result: (\w+), (.*)")
logfile = conf.get('checker_logfile',"log/smartchecker.log")


def get_log_by_date(loglines, start_date,end_date='',block=False):
    _lines = []

    flag_start = False
    for line in loglines:
        #print line
        if line.startswith(start_date):
            _lines.append(line)
            flag_start = True
        elif end_date and line.startswith(end_date):
            #print "found end_date"
            break
        elif flag_start:
            _lines.append(line)

    if block:
        return "".join(_lines)
    else:
        return _lines

class ResultStats(object):
    output_format = "%-12s\t%-15s\t%5s\t%5s\t%5s"
    output_fields = ('DATE','HOSTNAME','PASSED','FAILED','UNKOWN')

    def __init__(self,hostname,date,statsdata):
        """statsdata: 
        """
        self.hostname = hostname
        self.date = date
        self.data = {}

        for status,tnstr in statsdata:
            tns =tnstr.split(',')
            self.data[status]= tns

    def stats(self,status):
        if status not in self.data:
            return []
        else:
            return self.data[status]

    def count(self,status):
        if status in self.data:
            return len(self.data[status])
        else:
            return 0

    def output(self):
        rowstr = ResultStats.output_format % (self.date, 
                                              self.hostname,
                                              self.count('Passed'),
                                              self.count('Failed'), 
                                              self.count('Unknow'))
        print rowstr

    def __repr__(self):
        return "Stats: %s" % self.data

def parse_result_log(logblock):
    pat_hostdata = re.compile("([\d-]+).*?Result: (\w+), (.*)")
    pat_stat = re.compile("([Failed|Unknow|Passed]+):\[(.*?)\]")
    checkresult_stats = []

    #parse the hostname and the stats string.
    host_data = pat_hostdata.findall(logblock)

    ## hostdata: (date, hostname,"Failed:[xxx,xxx], Unknow:[zzz,zzz],Passed:[yyy,yyy])
    for date,host,statline in host_data:
        _stats = pat_stat.findall(statline)
        #print statline
        #print _stats
        checkresult_stats.append(ResultStats(host,date,_stats))

    return checkresult_stats

if __name__ == "__main__":
    if len(sys.argv)<2:
        print __doc__
        exit(1)
    args=sys.argv[1].split(',')

    if len(args)==2:
        start_date,end_date = args
    else:
        start_date = args[0]
        end_date = ''

    #print start_date,end_date

    loglines = file(logfile).readlines()
    lines=get_log_by_date(loglines,start_date,end_date)

    check_stats = parse_result_log("".join(lines))

    print ResultStats.output_format % ResultStats.output_fields
    for stats in check_stats:
        stats.output()