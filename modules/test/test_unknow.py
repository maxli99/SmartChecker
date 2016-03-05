name = 'test_unknow.py'
desc = "this check script result is unknow"
result = ''
info   = ''
errmsg = ''


def run(*args,**kwargs):
    return dict(result='unknown', info='hello')