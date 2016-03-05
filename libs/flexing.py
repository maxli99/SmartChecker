import re,textfsm
from hwparser import HardwareInfo

def get_ng_version(configlog):
    """This function will parse the NG version info from logfile.
    Input    config logfile
    return  a tuple include (major_version, release_version, hardware_version)
    example: ('3.2', '123445', '2')
    """
    version = None
    version_pat = re.compile("_NG([\d\._]+)_r(\d+)_AB(\d+)")

    try:
        log = ''.join(file(configlog).readlines())
    except IOError,e:
        print "IOError:", e
        exit(1)
    check = version_pat.search(log)

    if check:
        version = check.groups()
    return version

def get_hw_info(configlog):
    hwinfo = HardwareInfo()
    return hwinfo

if __name__ == "__main__":
    hw = get_hw_info('fake')
    print hw
