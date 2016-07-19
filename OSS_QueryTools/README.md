# 网管数据获取模块（应用于SmartChecker）介绍
## 模块开发目的
该模块主要目的是为了在SmartChecker中增加从网管数据库中获取数据的功能。在之前的SmartChecker中主要的数据来源是网元（包括MME/SAEGW等）的指令log。这些log可以解决很多监控任务，但还是存在一些限制，比如历史数据的收取，一些复杂数据的获取都需要网管数据来提供。针对这些需求，开发这个模块就是为了能提在SmartChecker中把网管数据库也能作为数据源。
## 软件开发及测试环境搭建
- 该模块使用python 2.7 + Oracle 客户端完成。
- 在python中安装cx_Oracle模块，该模块可在[Pypi网站下载(https://pypi.python.org/pypi/cx_Oracle)](https://pypi.python.org/pypi/cx_Oracle) ，目前下载安装的版本为cx_Oracle-5.1.2-10g.win32-py2.7.msi
- Oracle客户端可以在[http://www.oracle.com/technetwork/topics/winx64soft-089540.html](http://www.oracle.com/technetwork/topics/winx64soft-089540.html) 下载。目前使用的版本是instantclient-basic-windows.x64-12.1.0.2.0.zip。
## 模块介绍
- NSNG_OSS_config.py

    该脚本主要是定义下列class，在初始化时分别载入三个yaml配置文件(在当前目录的config子目录下）来定义和网管数据库相关的配置信息。这三个yaml文件内容会在后面详细介绍。


    class NSNG_OSS_config(object):

    def __init__(self):
        with open('config/OSS_Tables_column.json','r') as file_table:
            self.NSNG_OSS_tables_views = json.load(file_table)        

        with open('config/OSS_Databases.json','r') as file_databases:
            self.NSNG_OSS_database = json.load(file_databases)

        with open('config/OSS_NSNG.json','r') as file_ne:
            self.NSNG_OSS_NE = json.load(file_ne)


- OSS_query_v2.py

1.  该脚本首先定义了QueryOption类，类内包含软件执行查询所需的各个参数，详见下面的注释。QueryOption类还包含过滤命令行参数并赋值到类内参数的函数getQueryoptions。


    class QueryOptions(object):
    def __init__(self):
        self.selectelement = ''             # 网元名称      （'SHMME03BNK'/'SHSAEGW03BNK'/'ALL')
        self.startdate = ''                 # 查询的开始日期 ('2016/07/01')
        self.starttime = ''                 # 查询的开始时间（'09'(小时)）
        self.starttimemm = ''               # 查询的开始时间（'00'(分钟)）
        self.starttimeall = ''              # 查询的开始时间（'0910'(小时+分钟)）
        self.stopdate = ''                  # 查询的结束日期 ('2016/07/01')
        self.stoptime = ''                  # 查询的结束时间（'10'(小时)）
        self.stoptimemm = ''                # 查询的结束时间（'30'(分钟)）
        self.stoptimeall = ''               # 查询的开始时间（'1030'(小时+分钟)）
        self.selectperiod = '15'            # 查询的时间间隔（'15'/'60'(15分钟/每小时))
        self.selectunittype = 'NE'          # 查询的统计粒度（'MME'/'TA_ID','SAEGW'/'SSPROF_ID')
        self.selectcounters = ''            # 查询的Counters（'EPS_EME_ATTACH_FAIL',填入网管数据库里的对应Counter的列名;如果是查询ALARM数据库，请输入'ALARM'(表示查询所有告警)或者'ALARM,3604,2101'(指定告警号))
        self.reportfilename = ''            # 查询后输出的文件名 ('xxxx.json')
        self.localsave = '1'                # 查询数据是否需要输出到本地文件('0'/'1')


  
2.  脚本内还有其他一些函数。其中主要函数GenerateQueryData,用来完成查询网管数据库。查询结果是本地保存为json文件还是保存为dict变量（queryresult）中是由queryoption中的参数localsave决定。
保存到dict变量并作为调用GenerateQueryData函数的返回值，可实现该模块的API接口。
前者调用GenerateReportFile完成json文件保存，后者调用GenerateReportData产生dict对象。
            
- config/OSS_Databases.yaml

    该文件包括数据库连接建立所需的参数。其中name是数据库连接的名字，在后面介绍的OSS_NSNG.yaml中作为MME/SAEGW的数据库指定的标识。


    database:
    - {db: oss, ip: 127.0.0.1, name: MME_database, password: omc, port: '51063', user: omc}
    - {db: oss, ip: 127.0.0.1, name: SAEGW_database, password: omc, port: '51063', user: omc}





- config/OSS_NSNG.yaml

    该文件的目的是针对某一些项目上不同的网元可能会连接至不同的网管数据库的情况。其中name是数据库连接的名字，对应前面介绍的OSS_Databases.yaml中的name字段。


    NE:
    - {database: MME_database, name: SHMME03BNK}
    - {database: MME_database, name: SHMME04BNK}
    - {database: MME_database, name: SHMME05BNK}
    - {database: MME_database, name: SHMME06BNK}
    - {database: MME_database, name: SHMME07BNK}
    - {database: MME_database, name: SHMME08BNK}
    - {database: MME_database, name: SHMME09BNK}
    - {database: MME_database, name: SHMME10BNK}
    - {database: SAEGW_database, name: SHSAEGW03BNK}
    - {database: SAEGW_database, name: SHSAEGW04BNK}
    - {database: SAEGW_database, name: SHSAEGW05BNK}
    - {database: SAEGW_database, name: SHSAEGW06BNK}
    - {database: SAEGW_database, name: SHSAEGW07BNK}
    - {database: SAEGW_database, name: SHSAEGW08BNK}
    - {database: SAEGW_database, name: SHSAEGW09BNK}
    - {database: SAEGW_database, name: SHSAEGW10BNK}
    - {database: SAEGW_database, name: SHSAEGW11BNK}
    - {database: SAEGW_database, name: SHSAEGW12BNK}   


- config/OSS_Tables_column.yaml

    该文件的目的的提供网管数据库中每个跟测量有关的表格或视图（目前都是视图）的列信息。用于匹配查询参数中提供的Counter。在代码中通过Counter可以找到相应的Table或View的名称，建立SQL语句。

    
    NE_OSS_table_view:
    - tables:
        columns:
            column: [EPS_EME_ATTACH_SUCC_AUTH, EPS_EME_ATTACH_FAIL, EPS_EME_ATTACH_ATTEMPT,
                EPS_EME_ATTACH_SUCC_UNAUTH, EPS_EME_ATTACH_SUCC_UICCLESS, EPS_PAGING_VOLTE_ATTEMPT,
                EPS_PAGING_VOLTE_SUCC, EPS_PAGING_VOLTE_FAIL, EPS_TAU_FAIL_DUE_TA_RA_GRP_CHG,
                ...]
        name: PCOFNS_PS_MMMT_TA_RAW
    - tables:
        columns:
            column: [PDN_UEINIT_ACT_GW_MOD_BR_FAIL, PDN_UEINIT_ACT_UNSPEC_FAIL, FINS_ID,
                MCC_ID, MNC_ID, TA_ID, PERIOD_START_TIME, PERIOD_DURATION, CHANGE_NOTIFY_FAIL,
                EPS_DDBEARER_PDN_CONN_ATTEMPT, EPS_DDBEARER_PDN_CONN_SUCC, EPS_DDBEARER_PDN_CONN_DISCARD,
                ...]
        name: PCOFNS_PS_SMMT_TA_RAW    
    ...
    ...
    ...
    

## 使用说明
* 工具使用方式

命令执行方式：

1. 执行python脚本

Usage:  OSS_query_v2.py -D2016/07/19 -T0400 -d2016/07/19 -t0500 -eSHMME03BNK -cEPS_ATTACH_ATTEMPT,EPS_COMBINED_ATTACH_ATTEMPT -p60 -uMME -l1

其中命令行参数的解释如下：

    -D (Start Date   :2016/07/19)                       # 缺省值为当天日期
    -T (Start Time   :0400)                             # 缺省值为当前时间的前30m
    -d (Stop Date    :2016/07/19)                       # 缺省值为当天日期
    -t (Stop Time    :0500)                             # 缺省值为当前时间
    -e (Element      :SHMME03BNK/ALL)                   # 缺省值为ALL
    -c (Counter      :SUCC_COMBINED_ATTACH)             # 无缺省值，参数必须提供，多个指标以','分隔（','前后不要加空格）
    -p (Period       :15/60)                            # 缺省值为15
    -u (Unittype     :Type MME//TAC/session)            # 缺省值为MME
    -l (Localsave    :0/1 (Not/Yes)                     # 缺省值为1
    -R (ReportName   :'Report_xxxx.json')               # 缺省值为NESta_[网元]_[开始日期时间]_[结束日期时间]_[时间间隔]_[统计类型].json,存放目录在当前目录的Reports子目录内。
                                                        # 如：NESta_ALL_201607132351_201607140021_15_NE.json
                                                        # 如果是查询ALARM数据库，则是：NEALARM_[网元]_[开始日期时间]_[结束日期时间]_[时间间隔]_[统计类型].json

其中*Counter为必须提供的参数*。其他参数如果不提供，会自动提供缺省值。

如果查询告警数据库，请参考以下指令：
OSS_query_v2.py -D2016/07/19 -T1000 -d2016/07/19 -t1200 -eSHMME03BNK -cALARM,3604,2101 -p60 -uMME -l1 
OSS_query_v2.py -D2016/07/19 -T1000 -d2016/07/19 -t1200 -eSHSAEGW03BNK -cALARM -p60 -uSAEGW -l1 
如果查询SAEGW统计指标：
OSS_query_v2.py -D2016/07/19 -T1000 -d2016/07/19 -t1200 -eSHSAEGW03BNK -c RADIUS_ACCT_REQ_START_SENT,RADIUS_AUTH_RESP_REC, RADIUS_AUTH_REJ_REC -p60 -uSAEGW 

2. 执行exe文件

Usage： OSS_query_v2.exe -D2015/04/03 -T0400 -d2015/04/03 -t0500 -eSHMME03BNK -cSUCC_COMBINED_ATTACH -p60 -uNE -l1 -RNESta_ALL_201607132351_201607140021_15_NE.json

* API接口使用方式

接口调用模块的方式可参照下列代码：

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


## 模块各文件介绍
## 附件（配置文件内容介绍）