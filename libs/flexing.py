import re
from hwparser import HardwareInfo

class FlexiNG(object):
    pass

class FlexiNGVersion(object):
    pass
    
def get_ng_version(configlog):
    """This function will parse the NG version info from logfile.
parameters:
    configlog    config logfiler
return:
    return  a tuple include (major_version, release_version, hardware_version)
    
    example: ('3.2', '123445', '2')
    
    """
    version = None
    version_pat = re.compile("_NG([\d\._]+)_r(\d+)_AB(\d+)")
    if not configlog:
        return None
    try:
        lines=file(configlog).readlines()
        log = ''.join(lines)
    except IOError,e:
        print("IOError: %s" % e)
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
