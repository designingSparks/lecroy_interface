# coding: utf-8
'''
Created on 21.06.2016

@author: John.Schoenberger
'''
from __future__ import print_function, division
import os, sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from my_canvas import MyCanvas
from constants import BASEDIR, ICONDIR, DEBUG
import numpy as np

'''
TODO:
Create a toolbar.
Create a settings dialog
Try to create a cxfreeze build file.
'''
class Main(QMainWindow): #You can only add menus to QMainWindows
    def __init__(self):
        super(Main, self).__init__()

        #Set application icon
        iconfile = os.path.join(ICONDIR, 'icon_128x128.png')
        self.setWindowIcon(QIcon(iconfile))
#        self.createActions() #must happen before create menus
#        self.createToolBar()
#        self.createMenu()

        self.canvas = MyCanvas()
        self.vbox1 = QVBoxLayout() #used to display plugin
#        self.f = None #this is set in import_data(). Used by controller and loop gains  
        
        ######################################################
        #For the right hand side content - matplotlib bode plot
        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.canvas)
        vbox2.setContentsMargins(0,0,0,0) #remove margin between boxlayout and canvas
        widget = QWidget()
        
        #Use frames on either side of the horizontal splitter so you get a nice gripper for resizing
        leftframe = QFrame(widget)
        leftframe.setFrameShape(QFrame.StyledPanel)
        leftframe.setLayout(self.vbox1)
        leftframe.setMinimumWidth(150)
        leftframe.setMaximumWidth(200)
        
        rightframe = QFrame(widget)
        rightframe.setFrameShape(QFrame.StyledPanel)
        rightframe.setLayout(vbox2)
        
        hsplitter = QSplitter(Qt.Horizontal)
        hsplitter.addWidget(leftframe)
        hsplitter.addWidget(rightframe)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(hsplitter)
        
        widget.setLayout(hbox2) 
        self.setCentralWidget(widget)
#        self.create_file_menu()
#        self.create_plugin_menu()

    
        
        self.setWindowTitle('Ksync')
        self.resize(800, 600) #width, height
        self.show() #display and activate focus
        self.raise_() #comment out for mac
        
if __name__ == '__main__':
    print('Python 3')
    app = QApplication(sys.argv)
    gui = Main()
    x = np.linspace(1, 10, 11)
    y = x**2
    gui.canvas.ax1.plot(x,y)
    gui.canvas.draw()
    sys.exit(app.exec_())
    