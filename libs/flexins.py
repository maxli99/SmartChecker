import re

def get_ns_version(configlog):
	"""This function will parse the NS version info from logfile.
	Input  logfile
	return  a tuple include (ns_version)
	example: ('N5 1.19-3', 'N5 1.17-5','UNKNOWN')
	"""
	version = None
	#search the version info , the real version as default is mark with 'Y' in 'DEF' column
	version_pat = re.compile(r"ZWQO.*?      Y    Y",re.S)

	try:	
		log = ''.join(file(configlog).readlines())
        
		r=version_pat.search(log)
		if r:
			logpos=r.end()
			#version info is the line between pos:30--43
			version = log[logpos+30:logpos+43]
			
		return version
				
	except IOError,e:
		print("IOError: %s" % e)
		return 'UNKNOWN'
		
	

if __name__ == "__main__":
	nsversion = get_ns_version('..\\log\\test_ALL_NS_TN_check.log')
	print nsversion
