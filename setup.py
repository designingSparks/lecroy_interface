# coding: utf-8

# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

path = ["app"] + sys.path

options = {
    'build_exe': {
        #"path": path,
        'icon': 'res_icon.ico',
        'includes': 'atexit',
        'excludes': ['tk', 'ttk', 'tkinter', '_tkinter', 'scipy.io', 'scipy.sparse', 'scipy.lib', 'tcl', 'Tkconstants', 'PySide.QtNetwork',
          'nose', 'logging','pydoc_data'],
        'bin_excludes' : ['tcl85.dll', 'tk85.dll']
        #'excludes':['tk', '_tkagg', '_gtkagg', '_gtk', 'tcl']
    },

}

executables = [
    Executable('res_gui_main.py', base=base)
]

setup(name='Resistor Calculator',
      version='0.1',
      description='Calculate Parallel Resistor Combinations',
      options=options,
      executables=executables
      )
