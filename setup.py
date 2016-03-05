# -*- coding: utf-8 -*-

# A very simple setup script to create a single executable
#
# hello.py is a very simple 'Hello, world' type script which also displays the
# environment in which the script runs
#
# Run the build process :
#
#    'python setup.py build'
# or 
#    'python setup.py bdist_msi'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python

import sys
from cx_Freeze import setup, Executable
from smartchecker import __version__

options = {
    'build_exe': {
        'compressed': True,
        'include_files': [
            'readme.md',
            'checker.conf',
            'modules/',
            'log/',
            'checklist/',
        ],
        'includes' : ['libs','libs.flexing','textfsm'],
        'excludes' : ['Tkinter'],
        'path': sys.path + ['modules']
    }
}

executables = [
    Executable('smartchecker.py')
]

setup(name    = 'SmartChecker',
      version = __version__,
      author  = "Junest LX",
      author_email = "support@junest.com",
      options = options,      
      description ='Nokia Core Smart Checker',
      executables =executables      
      )
