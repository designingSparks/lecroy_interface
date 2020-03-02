#!/usr/bin/env python
# LeCrunch
# Copyright (C) 2010 Anthony LaTorre 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import socket
import struct
import h5py
import setup
from lecroy import LeCroyScope
from config import get_settings

def fetch(filename, nevents, runattrs=None):
    """
    Fetch and save waveform traces from the oscilloscope.

    Args:
        - filename: str
            Filename to store traces in (in hdf5 format).
        - nevents: int
            Number of triggered events to save in `filename`.
    """
    scope = LeCroyScope(setup.scope_ip, timeout=20.0)

    # turn off the display
    scope.send('display off')
    scope.check_last_command()

    # clear the output queue
    scope.clear()

    # get active channels
    channels = scope.getchannels()

    # get scope configuration
    settings = get_settings(scope)

    # get wave descriptors for each channel
    # important to do this before queue is primed!
    # need to trigger in order to get correct wave_array_count
    scope.trigger()

    time.sleep(5.0)

    wavedesc = {}
    for channel in channels:
        wavedesc[channel] = scope.getwavedesc(channel)

    # open up the output file
    f = h5py.File(filename, 'w')

    # set scope configuration
    for command, setting in settings.items():
        f.attrs[command] = setting

    if 'ON' in f.attrs['SEQUENCE']:
        sequence_count = int(f.attrs['SEQUENCE'].split(',')[1])

        if sequence_count < 1:
            raise Exception('sequence count must be a positive number.')
    else:
        sequence_count = 1

    for channel in channels:
        nsamples = wavedesc[channel]['wave_array_count']//sequence_count

        f.create_dataset('channel%i' % channel, (nevents, nsamples), dtype=wavedesc[channel]['dtype'], chunks=(max(1,min(100, nevents//100)), nsamples), compression='gzip')

        for key, value in wavedesc[channel].items():
            try:
                f['channel%i' % channel].attrs[key] = value
            except ValueError:
                pass

    if runattrs is not None:
        for name in runattrs:
            for key, value in runattrs[name].items():
                f[name].attrs[key] = value

    # start a timer
    time0 = time.time()

    try:
        i = 0
        while True:
            print '\rsaving event: %i' % i,
            sys.stdout.flush()

            try:
                scope.trigger()
                for channel in channels:
                    wave_array = scope.getwaveform(channel, wavedesc[channel])

                    if sequence_count > 1:
                        try:
                            f['channel%i' % channel][i:i+sequence_count] = \
                                wave_array.reshape(sequence_count, wave_array.size//sequence_count)
                        except ValueError:
                            f['channel%i' % channel][i:i+sequence_count] = \
                                wave_array.reshape(sequence_count, wave_array.size//sequence_count)[:len(f['channel%i' % channel])-i]
                    else:
                        f['channel%i' % channel][i] = wave_array

            except (socket.error, struct.error) as e:
                print '\n' + str(e)
                scope.clear()
                continue

            i += sequence_count

            if i >= nevents:
                print '\rsaving event: %i' % i,
                break

        print

    except KeyboardInterrupt:
        print '\nresizing datasets...'

        for channel in channels:
            f['channel%i' % channel].resize((i, wavedesc[channel]['wave_array_count']//sequence_count))
            
        raise

    finally:
        f.close()
        scope.clear()
        scope.send('display on')
        scope.check_last_command()

        elapsed = time.time() - time0

        if i > 0:
            print 'Completed %i events in %.3f seconds.' % (i, elapsed)
            print 'Averaged %.5f seconds per acquisition.' % (elapsed/i)
            print "Wrote to file '%s'." % filename

if __name__ == '__main__':
    import optparse
    import run_setup

    usage = "usage: %prog <filename/prefix> [-n] [-r]"
    parser = optparse.OptionParser(usage, version="%prog 0.1.0")
    parser.add_option("-n", type="int", dest="nevents",
                      help="number of events to store per run", default=1000)
    parser.add_option("-r", type="int", dest="nruns",
                      help="number of runs", default=1)
    parser.add_option("--time", action="store_true", dest="time",
                      help="append time string to filename", default=False)
    parser.add_option("-c", dest="run_config",
                      help="run configuration dictionary name", default=None)
    (options, args) = parser.parse_args()

    if len(args) < 1:
        sys.exit(parser.format_help())
    
    if options.nevents < 1 or options.nruns < 1:
        sys.exit("Please specify a number >= 1 for number of events/runs")

    if options.run_config is not None:
        options.run_config = getattr(run_setup, options.run_config)

        if 'file' not in options.run_config or \
                'dataset' not in options.run_config:
            raise AttributeError("run configuration must contain 'file' and 'dataset' keys")

        scope = LeCroyScope(setup.scope_ip, timeout=20.0)

        # clear the output queue
        scope.clear()

        # get active channels
        channels = scope.getchannels()

        # close the socket connection
        del scope

        runattrs = {'/' : {}}

        print '/'

        for key, fmt in options.run_config['file'].items():
            prompt = '/%s? ' % key
            while True:
                try:
                    runattrs['/'][key] = fmt(raw_input(prompt))
                except ValueError as e:
                    print e
                    continue
                break

        for name in ['channel%i' % i for i in channels]:
            runattrs[name] = {}

            print '/' + name

            for key, fmt in options.run_config['dataset'].items():
                prompt = '/%s.%s? ' % (name, key)
                while True:
                    try:
                        runattrs[name][key] = fmt(raw_input(prompt))
                    except ValueError as e:
                        print e
                        continue
                    break
    else:
        runattrs = None

    if options.nruns == 1 and not options.time:
        try:
            fetch(args[0], options.nevents, runattrs)
        except KeyboardInterrupt:
            pass
    else:
        import time
        import string

        for i in range(options.nruns):
            timestr = string.replace(time.asctime(time.localtime()), ' ', '-')
            filename = args[0] + '_' + timestr + '.hdf5'
            print '-' * 65
            print 'Saving to file %s' % filename
            print '-' * 65

            try:
                fetch(filename, options.nevents, runattrs)
            except KeyboardInterrupt:
                break
