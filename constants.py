# coding: utf-8
'''
Created on 15.10.2012

@author: john.schoenberger

Here you can see how to get the resource path for macos
https://github.com/pathomx/pathomx/blob/69a35b280e4275c688a92f86242261dd04757198/pathomx/utils.py

'''
import sys, os
DEBUG = True
SETTINGS_DIR = '.lecroy_plot'
SETTINGS_FILE = 'lecroy_plot_config.txt'

#Mac
# if getattr(sys, 'frozen', None): #if py2app or cxfreeze used
    # resource_dir = os.environ['RESOURCEPATH'] #e.g. my.app/Contents/Resources
    # ICONDIR = os.path.join(resource_dir, 'icons')
    # BASEDIR = resource_dir #datafiles specified in setup.py are copied here, not into the MacOS dir
    #Windows
# else:
#     BASEDIR = os.getcwd()
#     ICONDIR = os.path.join(BASEDIR, 'icons')

#Windows
if hasattr(sys, "frozen"): #if is a cx_freeze app
    BASEDIR = os.path.dirname(sys.executable)
    ICONDIR = os.path.join(BASEDIR, 'icons')
else:
    BASEDIR = os.path.dirname(__file__)
    ICONDIR = os.path.join(BASEDIR, 'icons')