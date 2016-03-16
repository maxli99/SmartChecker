#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: maxli
# @Date:   2016-03-10 14:10:40
# @Last Modified by:   maxli
# @Last Modified time: 2016-03-16 18:03:08

u'''
FlexiNS/MME S11 Throttling 检查
    - NS/MME软件版本为NS15 MP1或者更高版本
    - 已经关闭MME S11 Throttlling
描述：
    Flexi MME NS15 MP1 版本新增加了一个“S11 Throttling”功能
    该功能将在如下情况下被触发
    1、系统检查到Socket缓存溢出
    2、CPU利用率过高并且在S11口发送的数据包大于接收到的数据包
    当该功能被触发时，MME将产生14002告警并且停止所有S11口GTP数据包的重传
    这种行为将导致S11口大量信令流程无法完成并影响KPI
解决方法：
    关闭“S11 Throttling”功能
'''

import re
from libs.checker import ResultInfo, CheckStatus
from libs.log_spliter import LogSpliter


__author__ = 'maxli'
__email__ = 'max.1.li@nokia.com'
__date__ = '20160315'

# Mandatory variables
# -----------------------------------------------------
module_id = 'fnsbase.201603111030'
tag = ['flexins', 'china', 'S11', 'Throttling']
priority = 'Normal'
name = "TN_CN_20160212_S11_Throttling"
desc = __doc__
criteria = u'''
（1）MME软件版本为“N5 1.19-3”或高于该版本
（2）在“-ASWDIR/FNSINI/LNX968NX.INI”文件中，将参数“S11_THROTTLING_ENABLED”设置为0
'''

# -----------------------------------------------------

# Optional variables
# -----------------------------------------------------
# available target versions:
target_versions = ['N5 1.19-3']
check_commands = [
    ("ZWOI:;", "show the NS data of the parameters defined in the PRFILE"),
    ("ZWQO:CR;", "show the NS packages information"),
    ('ZDDE:IPDU,:"cat /opt/mme/conf/mmeGTPLBS-0x0968.ini",:;',
     "print the file content of LNX968NX.INI"),
]
know_version_identify_Patt = r"\s*(N\d+\s+\d+.\d+-\d+)\s*"
# -----------------------------------------------------

# The below functions is copied from TN-China_20151013-ns_mme_cause_code_mapping.py
# Thanks so much to Ouyang Mingli for ur sweet codes


def version_up_NS15_id(NsVersionId):
    up_id = 0
    version_id_Patt = r"\s*N(\d+)\s+\d+.\d+-\d+\s*"
    m = re.search(version_id_Patt, NsVersionId)
    if m:
        big_version_id = m.group(1)
        if int(big_version_id) >= 5:
            up_id = 1
    return up_id


def is_NS15_version_id(NsVersionId, Ns15VersionList):
    if NsVersionId in Ns15VersionList:
        return 1
    else:
        return 0


def Find_NS_MME_Patt_Return_Info_List(LogFile, CommandStr, InfoPatt, ReturnInfoLen):
    Command_start = False
    Command_end = False
    return_info_list = []
    Command_start_Patt = r"\s*[Z]?%s\s*" % (CommandStr)
    Command_start_Patt = Command_start_Patt.replace(':;', '[:]?;')
# print "Command_start_Patt =",Command_start_Patt
    Command_end_Patt = r"\s*COMMAND\s+EXECUTED\s*$"
    Find_Info_Patt = InfoPatt
# print "Find_Info_Patt =",Find_Info_Patt
    return_Len = ReturnInfoLen + 1
    fp = open(LogFile, 'r')
    for line in fp.readlines():
        if Command_start is False and Command_end is False:
            m = re.search(Command_start_Patt, line)
            if m:
                Command_start = True
                continue
        elif Command_start is True and Command_end is False:
            m0 = re.search(Command_end_Patt, line)
            m1 = re.search(Find_Info_Patt, line)
            if m0:
                Command_end = True
                continue
            if m1:
                for infoId in range(1, return_Len):
                    if m1.group(infoId):
                        return_info_list.append(m1.group(infoId))
                    else:
                        return_info_list.append('Not_Find_Infomation')
                continue
        else:
            break
    fp.close()
    return return_info_list


def is_throttling_on(logs):
    info = []
    status = CheckStatus.UNKNOWN
    pattern = re.compile("\s*S11_THROTTLING_ENABLED\s*=\s*(\d){1}")
    if len(logs) == 0:
        raise(u"日志文件中无法找到需要检测的信息，请确所认收集日志是是否执行“ZIBT:,,LNX968NX,INI,,,,A,;”。")
    for cmd_result in logs[0].result:
        matched = pattern.match(cmd_result)
        if matched:
            throttling = matched.group(1)
            if throttling == "0":
                status = CheckStatus.PASSED
                info.append(u"检查通过，S11 Throttling功能已经关闭")
                break
            else:
                status = CheckStatus.FAILED
                info.append(u"检查未通过，S11 Throttling功能处于开启状态，请尽快关闭该功能")
                break
    if status == CheckStatus.UNKNOWN:
        raise(u"日志文件中无法找到需要检测的信息，请确认所收集的日志是否正确。")
    return (status, info)


def run(logfile):
    Ns_version_Patt = r"\s*\S+\s+BU\s+\S+\s+(\w+\d+\s*\S+)\s+Y\s+Y\s*$"
    version = Find_NS_MME_Patt_Return_Info_List(
        logfile, 'WQO:CR;', Ns_version_Patt, 1)[0]

    result = ResultInfo(name)
    info = []
    errmsg = ''

    # ns version checking
    if is_NS15_version_id(version, target_versions) > 0 or version_up_NS15_id(version) > 0:
        info.append(u"    - NS/MME软件版本是[%s]。" % version)
    else:
        m = re.search(know_version_identify_Patt, version)
        if m:
            result.status = CheckStatus.PASSED
            info.append(u"    - NS/MME软件版本是[%s]，不存在该问题。" % version)
        else:
            result.status = CheckStatus.UNKNOWN
            info.append(u"    - NS/MME软件版本是[%s]，无法准确判断版本信息，请人工核实。" % version)
            if version == '':
                errmsg = u'无法判断版本信息'
        result.update(info=info, error=errmsg)
        return result

    # throttling feature checking
    try:
        logspt = LogSpliter()
        logspt.load(logfile)
        logs = logspt.get_log(
            "DDE:IPDUcat /opt/mme/conf/mmeGTPLBS-0x0968.ini", fuzzy=True)
    except Exception as e:
        errmsg = "日志文件无法加载，请检查命令参数是否正确！"
        result.status = CheckStatus.UNKNOWN
    else:
        try:
            result.status, extra_info = is_throttling_on(logs)
            info.extend(extra_info)
        except Exception as e:
            errmsg = str(e)
            result.status = CheckStatus.UNKNOWN
    result.update(info=info, error=errmsg)
    return result
