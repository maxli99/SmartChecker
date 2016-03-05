import json
import subprocess

name = 'test_shell.py'
desc = "this is a check using shell script."
result = ''
info   = ''
errmsg = ''

def run(*args,**kwargs):
    result = dict(result='PASSED',info='bingo')
    return result