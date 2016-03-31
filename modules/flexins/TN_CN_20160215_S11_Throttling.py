#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: maxli
# @Date:   2016-03-10 14:10:40
# @Last Modified by:   Max Li
# @Last Modified time: 2016-03-31 12:58:06

u'''
FlexiNS/MME S11 Throttling 检查
    1、NS/MME软件版本为NS15 MP1或者更高版本
    2、已经关闭MME S11 Throttlling
问题原理：
    Flexi MME NS15 MP1 版本新增加了一个“S11 Throttling”功能
    该功能将在如下情况下被触发
    1、系统检查到Socket缓存溢出
    2、CPU利用率过高并且在S11口发送的数据包大于接收到的数据包
    当该功能被触发时，MME将产生14002告警并且停止所有S11口GTP数据包的重传
    这种行为将导致S11口大量信令流程无法完成并影响KPI
解决方法：
    这个问题是 NS15 MP1 引入的问题， TS 建议关闭此功能，即在配置文件LNX968NX.INI中设置
    S11_THROTTLING_ENABLED=0。关闭过程需要重启系统，无在线修改的方法，因此，请各个已经
    升级至 NS15MP1 的项目关闭此功能，避免出现影响业务的故障。
影响范围：
    MME NS15 MP1 版本。
风险评估：
    该问题风险评估为“高”,NS3.15 MP1 版本存在此问题。
'''

import re

from libs.checker import ResultInfo, CheckStatus
from libs.log_spliter import LogSpliter
from libs.infocache import shareinfo
from libs.tools import debugmsg as simple_debug

__author__ = 'maxli'
__email__ = 'max.1.li@nokia.com'
__date__ = '20160315'

# Mandatory variables
# -----------------------------------------------------
module_id = 'fnsbase.201603281030'
tag = ['flexins', 'china', 'S11', 'Throttling']
priority = 'Normal'
name = "TN_CN_20160212_S11_Throttling"
desc = __doc__
criteria = u'''
（1）MME软件版本为“N5 1.19-3”或高于该版本
（2）在“-ASWDIR/FNSINI/LNX968NX.INI”文件中，将参数“S11_THROTTLING_ENABLED”设置为0
'''

# Optional variables
# -----------------------------------------------------
# available target versions:
target_versions = ['N5 1.19-3']
check_commands = [
    ('ZDDE:IPDU,:"cat /opt/mme/conf/mmeGTPLBS-0x0968.ini",:;',
     "print the file content of LNX968NX.INI"),
]


def debugmsg(msg):
    """A better formet of debugmsg

    pring debug message with module name and line number

    Arguments:
        msg { str } -- the message need to output
    """
    import sys
    line = sys._getframe().f_back.f_lineno
    simple_debug("[module: %-20s][line: %-4s] - %s" % (name, line, msg))


def is_throttling_on(logs):
    """check whether the s11 throttling function is turned on or not

    Search a specified field of command 'ZDDE:IPDU,:"cat /opt/mme/conf/mmeGTPLBS-0x0968.ini",:;',
    and return the result of the inspection.

    Arguments:
        logs { [log_speliter.LogSegment] } -- the log_segment of the required command

    Raises:
        Exception -- raise a normal exception if something wrong in the log

    Returns:
        { (status, [info]) }
    """
    info = []
    status = CheckStatus.UNKNOWN
    pattern = re.compile("\s*S11_THROTTLING_ENABLED\s*=\s*(\d){1}")
    if len(logs) == 0:
        debugmsg("can not get the s11 throttling related command in the log file")
        raise Exception(u'日志文件中无法找到需要检测的信息，请确所认收集日志是是否执行“ZDDE:IPDU,:"cat /opt/mme/conf/mmeGTPLBS-0x0968.ini",:;”。')
    for cmd_result in logs[0].result:
        matched = pattern.match(cmd_result)
        if matched:
            throttling = matched.group(1)
            debugmsg("current throtlling is set to [%s]" % throttling)
            if throttling == "0":
                status = CheckStatus.PASSED
                info.append(u"检查通过，S11 Throttling功能已经关闭\n")
                break
            else:
                status = CheckStatus.FAILED
                info.append(u"检查未通过，S11 Throttling功能处于开启状态，请尽快关闭该功能\n")
                break
    if status == CheckStatus.UNKNOWN:
        debugmsg("the command output does not contain the required info, please check the log manually")
        raise Exception(u"日志文件中无法找到需要检测的信息，请确认所收集的日志是否正确。")
    return (status, info)


def run(logfile):
    """module entry of S11 Throttling validation

    Parse the log file and return the result of the validation.

    Arguments:
        logfile { str } -- the name of the log file

    Returns:
        { libs.checker.ResultInfo }
    """
    result = ResultInfo(name)
    info = []
    errmsg = ''

    # MME version
    try:
        ns_version = ""
        ns_version = shareinfo.get('ELEMENT').version['BU']
        debugmsg("get the ns version [%s]" % ns_version)
        info.append(u"当前NS/MME软件版本是[%s]\n" % ns_version)
        if ns_version in target_versions:
            debugmsg("ns version is in the target versions")
            info.append(u"当前NS/MME软件版本存在Throttling功能开启风险\n")
        else:
            debugmsg("ns version is not in the target versions")
            info.append(u"当前NS/MME软件版本不存在Throttling功能开启风险\n")
            result.status = CheckStatus.PASSED
            result.update(info=info, error=errmsg)
            return result
    except Exception as e:
        debugmsg("Can not get a correct ns version info from log, only got [%s]" % ns_version)
        result.status = CheckStatus.UNKNOWN
        info.append(u"NS/MME软件版本是[%s]，无法准确判断版本信息，请人工核实。\n" % ns_version)
        errmsg = u'无法获取软件版本信息'
        result.update(info=info, error=errmsg)
        return result

    # throttling feature checking
    try:
        logspt = LogSpliter()
        logspt.load(logfile)
        logs = logspt.get_log(
            "DDE:IPDUcat /opt/mme/conf/mmeGTPLBS-0x0968.ini", fuzzy=True)
    except Exception as e:
        info.append(u"日志文件无法加载，请检查命令参数是否正确！\n")
        errmsg = u"日志文件无法加载，请检查命令参数是否正确！"
        result.status = CheckStatus.UNKNOWN
    else:
        try:
            result.status, extra_info = is_throttling_on(logs)
            info.extend(extra_info)
        except Exception as e:
            info.append("%s\n" % e.args[0])
            errmsg = e.args[0]
            result.status = CheckStatus.UNKNOWN
    result.update(info=info, error=errmsg)
    return result
