from libs.nglib import *

name = 'tn0074_leap_second.py'
desc = "this"
result = ''
info   = ''
errmsg = ''


def run(configlog,*args,**kwargs):
    info = get_ng_version(configlog)
    return dict(result=FAILED,info=info)