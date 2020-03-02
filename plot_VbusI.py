# -- coding: utf-8 --
'''
Created on Nov 14, 2018

@author: john.schoenberger
'''
from __future__ import print_function, division
from lecroy_interface import LecroyInterface
from matplotlib.pyplot import *
SCOPE_IP = '192.168.1.1'


if __name__ == '__main__':
    lecroy = LecroyInterface(SCOPE_IP)
    t1, data1 = lecroy.measure_channel(1)
    t2, data2 = lecroy.measure_channel(4)
    
    fig, ax1 = subplots()
    color = 'tab:red'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Vbus (V)', color=color)
    ax1.plot(t1, data1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    
    color = 'tab:blue'
    ax2.set_ylabel('Iin (mA)', color=color)  # we already handled the x-label with ax1
    ax2.plot(t2, data2*1000, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    grid(True)
    show()