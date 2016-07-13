from distutils.core import setup
import py2exe

includes = ["decimal"]

options ={'py2exe' :  
            {'dll_excludes': ['w9xpopen.exe'], #w9xpopen is the file for windows9x platform, we can exclude it.
            }
         }  


setup(
    options = options,
    console = ['OSS_query_v2.py'],
    data_files = [('',
        ['oraocci12.dll','oraocci12.sym','oraocci12d.dll','oraocci12d.sym']) #inclue TestDll.dll to dist folder
        ]
)