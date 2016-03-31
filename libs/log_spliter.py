#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: maxli
# @Date:   2015-08-20 12:37:09
# @Last Modified by:   Max Li
# @Last Modified time: 2016-03-31 12:53:17

import os
import sys
import re

if sys.version_info.major == 3:
    PY3 = True
else:
    PY3 = False

LOG_TYPE_FLEXI_NS = "flexins"
LOG_TYPE_FLEXI_NG = "flexing"

class SpliterException(Exception):
    """Abstract base class shared by all exceptions."""
    pass

class SpliterLogFileException(SpliterException):
    """log file exception."""
    pass

class SpliterClassException(SpliterException):
    """class exception."""
    pass

class SpliterInterfaceException(SpliterException):
    """Interface exception."""
    pass


class LogSegment(object):
    def __init__(self, command, result):
        self.__command = command
        self.__result = result

    @property
    def command(self):
        return self.__command

    @property
    def result(self):
        return self.__result

    def __str__(self):
        _str = "COMMAND:\n"
        _str += "   %s\n"%self.__command
        _str += "RESULT:\n"
        for one_line_result in self.__result:
            _str += "   %s\n"%one_line_result
        return _str


class SpliterBase(object):
    def __init__(self):
        super(SpliterBase, self).__init__()
        self._log = []
        self._raw_log = ""
        self._log_file = ""
        self.__index = 0

    def load(self, file_name):
        if not os.path.exists(file_name):
            raise SpliterLogFileException("%s does not exist"%file_name)
        if not os.path.isfile(file_name):
            raise SpliterLogFileException("%s is not a file"%file_name)
        if not os.access(file_name, os.R_OK):
            raise SpliterLogFileException("%s is not readable"%file_name)

        self._log_file = file_name
        if PY3:
            with open(file_name, encoding='utf_8_sig') as f:
                try:
                    self._raw_log = f.read()
                except Exception as e:
                    raise SpliterLogFileException(e)
        else:
            with open(file_name) as f:
                try:
                    self._raw_log = f.read()
                    self.__remove_BOM()
                except Exception as e:
                    raise SpliterLogFileException(e)
        self.parse()

    def get_raw_log(self):
        return self._raw_log

    def get_log(self, command, match_head = False, fuzzy = False):
        logs = []
        if match_head and fuzzy:
            raise SpliterInterfaceException("Do not use match_head and fuzzy simultaneously")
        if command[0] != "Z":
            command = "Z%s"%command
        pattern = "%s"%command
        if match_head:
            pattern = "%s.*"%command
        if fuzzy:
            pattern = (".*").join(command)
        regex = re.compile(pattern)
        for log in self._log:
            if regex.match(log.command):
                logs.append(log)
        return logs

    def __remove_BOM(self):
        # Some windows editor would automatically insert "\xEF\xBB\xBF"
        # into the file to identify the utf-8 codec, we need to remove
        # it to get the pure log content.
        # NOTE, this method needs to be improved if other coedc's BOM
        # is to be dealed with.
        if self._raw_log[0:3] == "\xEF\xBB\xBF":
            self._raw_log = self._raw_log[3:]

    def __str__(self):
        _str = ""
        for log in self._log:
            _str += str(log)
        return _str

    def __len__(self):
        return len(self._log)

    def __iter__(self):
        self.__index = 0
        return self

    #for python 3
    def __next__(self):
        if self.__index >= len(self._log):
            raise StopIteration
        else:
            self.__index += 1
            return self._log[self.__index-1]

    #for python 2
    def next(self):
        return self.__next__()

    def parse(self):
        raise SpliterClassException("unknown splliter type %s"%type)


class FlexiNSSpliter(SpliterBase):
    def __init__(self):
        super(FlexiNSSpliter, self).__init__()
        self.__command_start_patten = r"^< .*"
        self.__command_execute_patten = r"(< )?.*;$"
        self.__command_stop_patten = r".*<[_\w]{2}_>$"

    def __get_command(self, command_line):
        return command_line if command_line[0:2] != "< " else command_line[2:]

    def __get_current_command_set(self, command_line):
        raw_set = re.findall(r"<[\w|_]{3}>", command_line)
        if len(raw_set) == 0:
            return ""
        return raw_set[0][1:4].replace("_", "")

    def parse(self):
        log_lines = self._raw_log.split("\n")
        current_command_set = ""
        current_command = ""
        current_result = []
        start_flag = False
        for log_line in log_lines:
            log_line = log_line.rstrip("\r\n\t ")
            # command stop
            if re.match(self.__command_stop_patten, log_line):
                current_command_set = self.__get_current_command_set(log_line)
                if start_flag:
                    if current_command[0] != "Z":
                        current_command = "Z%s"%current_command
                    self._log.append(LogSegment(current_command, current_result))
                start_flag = False
                current_result = []

            # command execute
            elif re.match(self.__command_execute_patten, log_line):
                current_command = self.__get_command(log_line)
                #force return to root command set
                if current_command[0] != "Z" and current_command[0:len(current_command_set)] != current_command_set:
                    current_command = "%s%s"%(current_command_set, current_command)
                start_flag = True
                current_result = []

            # start a new command
            elif re.match(self.__command_start_patten, log_line):
                #refresh the current command set with "Z"
                if re.match(r"< Z.*", log_line):
                    current_command_set = ""
                start_flag = False

            # comman output
            else:
                if start_flag:
                    current_result.append(log_line)


class FlexiNGSpliter(SpliterBase):
    def __init__(self):
        super(FlexiNGSpliter, self).__init__()

    def parse(self):
        raise SpliterClassException("does not implement")


class LogSpliter(object):
    def __new__(cls, type=LOG_TYPE_FLEXI_NS):
        if type == LOG_TYPE_FLEXI_NS:
            ob = object.__new__(FlexiNSSpliter)
        elif type == LOG_TYPE_FLEXI_NG:
            ob = object.__new__(FlexiNGSpliter)
        else:
            raise SpliterClassException("unknown splliter type %s"%type)
        ob.__init__()
        return ob
