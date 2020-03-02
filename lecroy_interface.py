'''
Created on 03.05.2012

@author: john.schoenberger
'''
from __future__ import print_function, division
from lecrunch.lecroy import LeCroyScope
from lecrunch.config import set_settings
from lecrunch.config import get_settings
import socket
from matplotlib.pyplot import *

from numpy import linspace
import csv

commands = ['TIME_DIV', 'COMM_FORMAT', 'COMM_HEADER', 'COMM_ORDER'] + \
    ['TRIG_DELAY', 'TRIG_SELECT', 'TRIG_MODE', 'TRIG_PATTERN', 'SEQUENCE'] + \
    ['C%i:COUPLING' % i for i in range(1,5)] + \
    ['C%i:VOLT_DIV' % i for i in range(1,5)] + \
    ['C%i:OFFSET' % i for i in range(1,5)] + \
    ['C%i:TRIG_COUPLING' % i for i in range(1,5)] + \
    ['C%i:TRIG_LEVEL' % i for i in range(1,5)] + \
    ['C%i:TRIG_SLOPE' % i for i in range(1,5)] + \
    ['C%i:TRACE' % i for i in range(1,5)]
    
        
class LecroyInterface(LeCroyScope):
    
    def __init__(self, ip_address):
        LeCroyScope.__init__(self, ip_address, timeout = 5)
        
        #May possibly help if you get a timeout, then close an ipython window
        #http://stackoverflow.com/questions/3905832/python-closing-a-socket-already-opened-by-a-precedent-python-program-or-dirty
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        
        #self.scope = LeCroyScope(ip_address, timeout=20.0)
        #set channels 1,2 to AC coupling
        #self.set_settings({'C1:COUPLING':'C1:CPL A1M'}) #A1M or D1M
        #self.set_settings({'C2:COUPLING':'C2:CPL A1M'})
    
    def __del__(self):
        print('Scope connection deleted')
        #TODO: close the socket?
        
    def set_timebase(self, t):
        '''Set the timebase of scope to the value t.
        '''
        self.set_settings({'TIME_DIV':'TDIV %f' % t})
        
        
    def measure_channel(self, channel):
        
        #print 'Plotting channel', channel
        desc = self.getwavedesc(channel)
        dy = desc['vertical_gain']
        dx = desc['horiz_interval'] #between each sample
        delta_y = desc['vertical_offset'] #yoffset
        n_samples = desc['wave_array_count'] #number of samples
    
        data = self.getwaveform(channel, desc)*dy - delta_y
        
        #Calculate the time axis
        t = linspace(0, n_samples-1, n_samples)*dx #don't need to subtract delta_x unless you want to start with a -ve time
#        print 't', t
#        T = n_samples*dx #length of the entire time slice
#        print 'T', T
        
        return t, data
    
    
    def save_data(self, data1, data2, filename):
        '''Saves the data in arrays data1, data2 to file
        '''
        data = [(data1[i], data2[i]) for i in range(data1.size)]
        f = open(filename, 'wb')
        out = csv.writer(f, delimiter=',')
        out.writerows(data)
        f.close()
        
    ##Untested
    def set_trigger(self, channel, voltage):
        '''Command for the Lecroy to set the trigger level of *channel* to *voltage*
        This function is not actually used
        '''
        cmda = 'C%i:TRIG_LEVEL' % channel
        cmdb = 'C%i:TRLV %f V' % (channel, voltage)
        cmd = {cmda:cmdb} #make as a dictionary
        print(cmd)
        self.set_settings(cmd)

    
    
    #############################################
    #These were originally from lecrunch.config
    #############################################
    def get_settings(self):
        settings = {}
        for command in commands:
            self.send(command + '?')
            settings[command] = self.recv().strip()
            self.check_last_command()
        return settings
    
    def set_settings(self, settings):
        for command, setting in settings.items():
            print('sending {}'.format(command))
            self.send(setting)
            self.check_last_command()
            
            
if __name__ == '__main__':
    SCOPE_IP = '192.168.1.1'
    lecroy = LecroyInterface(SCOPE_IP)
    t1, data1 = lecroy.measure_channel(1)
    plot(t1, data1)
    grid(True)
    show()