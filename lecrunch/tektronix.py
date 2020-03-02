import socket
import re
import numpy as np

preamble_fields = {'BYT_NR': int, # data width for waveform
                   'BIT_NR': int, # number of bits per waveform point
                   'ENCDG' : str, # encoding of waveform (binary/ascii)
                   'BN_FMT': str, # binary format of waveform
                   'BYT_OR': str, # ordering of waveform data bytes (LSB/MSB)
                   'NR_PT' : int, # record length of record waveform
                   'WFID'  : str, # description string of waveform
                   'PT_FMT': str, # format of reverence waveform (Y/ENV)
                   'XINCR' : float,
                   'PT_OFF': int,
                   'XZERO' : float,
                   'XUNIT' : str,
                   'YMULT' : float,
                   'YZERO' : float,
                   'YOFF'  : float,
                   'YUNIT' : str,
                   'NR_FR' : int }

header_regex = re.compile('(?::HEADER ){0,1}(\d)')

def get_dtype(preamble):
    """Returns the numpy dtype for the raw waveform data given the preamble."""
    if preamble['BYT_OR'] == 'MSB':
        byteorder = '>'
    elif preamble['BYT_OR'] == 'LSB':
        byteorder = '<'
    else:
        raise Exception('unknown byte order %s' % preamble['BYT_OR'])

    if preamble['BN_FMT'] == 'RI':
        signedchar = 'i'
    elif preamble['BN_FMT'] == 'RP':
        signedchar = 'u'
    else:
        raise Exception('unknown binary format string %s' % preamble['BN_FMT'])

    return byteorder + signedchar + str(preamble['BYT_NR'])

def convert_waveform(waveform, preamble):
    """Converts a waveform returned by the scope into voltage values."""
    return preamble['YZERO'] + (waveform - preamble['YOFF'])*preamble['YMULT']

def build_time_array(preamble):
    return preamble['XZERO'] + (np.arange(preamble['NR_PT']) - preamble['PT_OFF'])*preamble['XINCR']

class TekScope(object):
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,port))

    def send(self, msg):
        if not msg.endswith('\n'):
            msg += '\n'

        self.sock.sendall(msg)

    def clear(self):
        self.send('*cls')

    def recv(self, size=None):
        buffer = ''

        if size is None:
            while True:
                buffer += self.sock.recv(4096)

                if buffer.endswith('\n'):
                    break
        else:
            while len(buffer) < size:
                buffer += self.sock.recv(min(size-len(buffer),4096))

        return buffer

    def query(self, msg):
        """Sends a query to the oscilloscope and returns the response."""
        self.send(msg)
        return self.recv().strip()

    def enable_fastframe(self, count):
        self.send('horizontal:fastframe:state 1')
        self.send('horizontal:fastframe:count %i' % count)

    def set_sequence_mode(self):
        """Sets the oscilloscope in single acquisition mode."""
        self.send('acquire:stopafter sequence\n')

    def acquire(self):
        """Trigger and acquire a new waveform."""
        self.send('acquire:state run\n')

        acquire_regex = re.compile('(?::ACQUIRE:STATE ){0,1}(\d)')

        while int(acquire_regex.match(self.query('acquire:state?')).group(1)):
            pass

    def get_preamble(self, channel):
        """Returns a dictionary containing information about the waveform
        format for a channel."""
        header = int(header_regex.match(self.query('header?\n')).group(1))

        # turn header on so that we know preamble field names
        self.send('header 1\n')

        source = self.query('data:source?')

        self.send('data:source ch%i\n' % channel)

        preamble = {}
        for s in self.query('wfmpre?\n').strip()[8:].split(';'):
            key, value = s.split(' ',1)

            preamble[key] = preamble_fields[key](value)

        # reset header format and data:source
        self.send('header %i' % header)
        self.send(source)

        return preamble

    def get_active_channels(self):
        """Returns a list of the active (displayed) channel numbers."""
        header = int(header_regex.match(self.query('header?\n')).group(1))

        self.send('header 1\n')

        channels = []
        for s in self.query('select?').strip()[8:].split(';'):
            m = re.match('CH(\d) (\d)', s)

            if m is not None:
                ch, state = map(int,m.groups())

                if state != 0:
                    channels.append(ch)

        self.send('header %i' % header)

        return channels

    def get_waveform(self, channel, dtype=None):
        """Returns the waveform from channel as a numpy array. If dtype is
        specified, the function does not need to query the scope for the data
        format which will be much quicker."""
        header = int(header_regex.match(self.query('header?\n')).group(1))

        self.send('header 0\n')

        # not sure what pt_fmt env is, so we'll always transmit
        # in pt_fmt y format
        self.send('wfmpre:pt_fmt y\n')

        self.send('data:source ch%i\n' % channel)

        if dtype is None:
            dtype = get_dtype(self.get_preamble(channel))

        self.send('curve?\n')

        # the initial response from curve looks like '#x<y>' where x is
        # the number of y characters, and y is the number of bytes in the
        # waveform.
        # for example: '#41000' at the beginning of a curve? response means
        # that there are 1000 bytes in the waveform
        x = self.sock.recv(2)

        assert x.startswith('#')

        y = int(self.sock.recv(int(x[1])))

        waveform = np.fromstring(self.recv(y),dtype)

        # messages end with a newline
        eom = self.sock.recv(1024)

        if eom != '\n':
            raise Exception("eom != '\n'")

        self.send('header %i' % header)

        return waveform

if __name__ == '__main__':
    import h5py
    import optparse
    import setup
    import sys
    import os
    import math
    import time

    usage = 'usage: %prog <filename> [-n]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-n', type='int', dest='nevents',
                      help='number of events per run', default=1000)
    parser.add_option('-r', type='int', dest='nruns',
                      help='number of runs', default=1)
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit(parser.format_help())

    if options.nevents < 1 or options.nruns < 1:
        sys.exit('nevents and nruns must be greater than 1.')

    scope = TekScope(setup.scope_ip, setup.port)

    scope.clear()

    root, ext = os.path.splitext(args[0])

    if ext == '':
        ext = '.hdf5'

    for run in range(options.nruns):
        if options.nruns > 1:
            fileid = '_' + str(run).zfill(int(math.log10(options.nruns))+1)
        else:
            fileid = ''

        filename = root + fileid + ext

        print 'saving to %s' % filename

        t0 = time.time()

        with h5py.File(filename, 'w') as f:
            f.attrs['settings'] = scope.query('*lrn?')

            active_channels = scope.get_active_channels()

            for channel in active_channels:
                preamble = scope.get_preamble(channel)

                dataset = f.create_dataset('channel%i' % channel, (options.nevents, preamble['NR_PT']), dtype=get_dtype(preamble), chunks=(max(1,min(100, options.nevents//100)), preamble['NR_PT']), compression='gzip')

                for key, value in preamble.iteritems():
                    dataset.attrs[key] = value

            # enable single acquisition mode
            scope.set_sequence_mode()

            scope.send('header 0\n')

            fastframe_state = int(scope.query('horizontal:fastframe:state?'))
            fastframe_count = int(scope.query('horizontal:fastframe:count?'))

            i = 0
            try:
                while i < options.nevents:
                    print '\rsaving event: %i' % (i+1),
                    sys.stdout.flush()

                    scope.acquire()

                    if fastframe_state:
                        n = min(fastframe_count,options.nevents-i)
                    else:
                        n = 1

                    for channel in active_channels:
                        dataset = f['channel%i' % channel]

                        data = scope.get_waveform(channel, dataset.dtype)

                        if fastframe_state:
                            data = data.reshape((fastframe_count,-1))
                            dataset[i:i+n] = data[:n]
                        else:
                            dataset[i] = data

                    i += n
            except KeyboardInterrupt:
                print
                print 'resizing datasets...'

                for channel in active_channels:
                    dataset = f['channel%i' % channel]
                    dataset.resize((i,dataset.shape[1]))

                break
            else:
                print

        elapsed = time.time() - t0

        print 'saved %s. elapsed %f sec.' % (filename,elapsed)
