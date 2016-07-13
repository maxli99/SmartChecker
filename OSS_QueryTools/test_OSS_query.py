import json
from OSS_query_v2 import *

if __name__ == "__main__":
    queryoptioninfo = QueryOptions()

    queryoptioninfo.selectelement = 'SHMME03BNK' 
    queryoptioninfo.startdate = '2016/07/12'
    queryoptioninfo.starttime = '12'
    queryoptioninfo.starttimemm = '00' 
    queryoptioninfo.starttimeall = '1200'
    queryoptioninfo.stopdate = '2016/07/12' 
    queryoptioninfo.stoptime = '13'
    queryoptioninfo.stoptimemm = '00'
    queryoptioninfo.stoptimeall = '1300'
    queryoptioninfo.selectperiod = '15'
    queryoptioninfo.selectunittype = 'NE'
    queryoptioninfo.selectcounters = 'EPS_EME_ATTACH_SUCC_AUTH'
    queryoptioninfo.localsave = '0'
    queryoptioninfo.reportfilename = 'NE_test.json'
    queryresult , result = GenerateQueryData(queryoptioninfo)

    print 'result : ' + result 
    print queryresult
    if (result != ''):
        print result + ' , please check parameter or contact the code developer.'  
        exit()
    else:
        json.dumps(queryresult)
