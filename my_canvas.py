'''

 
@author: john
'''

from __future__ import division
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT #Agg
from numpy import *
from itertools import cycle 


#from enum import Enum
#DRAG_MODE = Enum('none','cursor','zoom')

#Default line style
STYLES = [{'lw': 2, 'c': 'b'}, {'lw': 2, 'c': 'g'}, {'lw': 2, 'c': 'r'}]


class MyCanvas(FigureCanvas):
    '''
    Creates a figure with two subplots for displaying the gain and phase plots of the controller
    '''
    def __init__(self, parent=None):
        

        fig = Figure() #This works!! Supplying any additional arguments causes the blit to fail
        FigureCanvas.__init__(self, fig)
        fig.patch.set_facecolor([1,1,1])
        
        #fig.patch.set_facecolor(None)
        #fig.patch.set_alpha(0)
        
        self.setParent(parent)

        self.ax1 = fig.add_subplot(211)
        self.ax1.grid()
        self.ax1.grid(which='minor')
        self.ax2 = fig.add_subplot(212)
        self.ax2.grid()
        self.ax2.grid(which='minor')
        self.show()
    
    def add_plot(self, f, mag, phase, xlabel=None, ax1_lab=None, ax2_lab=None):
        '''Plots the plant transfer function
        '''
        
#         if styles is None:
#             styles = STYLES
        ls = cycle(STYLES).next()
        
        
        self.ax1.semilogx(f, mag, **ls)
        if ax1_lab is not None:
            self.ax1.set_ylabel(ax1_lab)
            
        self.ax2.semilogx(f, phase, **ls)
        if ax1_lab is not None:
            self.ax2.set_ylabel(ax2_lab)
        
        if xlabel is not None:
            self.ax2.set_xlabel(xlabel)
             
        #self.canvas.draw()
        self.draw()
        
     
#if __name__ == '__main__':
#    
#    app = QApplication(sys.argv)
#    
#    f = logspace(0, 2, 21)
#    mag = f**2
#    phase = sin(2*pi*f)
#    
#    b = BodeCanvas()
#    style1 = {'linewidth': 2}
#    b.add_plot(f, mag, phase, xlabel='Frequency (Hz)', ax1_lab='Magnitude (dB)', ax2_lab='Phase ($^\circ$)')
#    #b.fig.savefig('bode_pipp.eps')
#    print 'Executing'
#    app.exec_()