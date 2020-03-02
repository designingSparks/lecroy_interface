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
"""
Save/load settings from a LeCroy X-stream oscilloscope. Settings are saved as
a python dictionary in two ways: pickled to a stand-alone file, or attached as
attributes to a hdf5 file. Settings can be loaded from either source.

Examples:
    Save/load settings to/from a pickled dictionary.
    >>> config.py save mysettings.pkl
    >>> config.py load mysettings.pkl
    sending TIME_DIV
    sending COMM_FORMAT
    ...

    Save/load settings from a dataset.
    >>> fetch.py test.hdf5 -n 100
    Saving event: 1000
    Completed 1000 events in 15.302 seconds.
    Averaged 0.01530 seconds per acquisition.
    Wrote to file 'test.hdf5'.
    >>> settings.py load test.hdf5
    sending TIME_DIV
    sending COMM_FORMAT
    ...
"""

commands = ['TIME_DIV', 'COMM_FORMAT', 'COMM_HEADER', 'COMM_ORDER'] + \
    ['TRIG_DELAY', 'TRIG_SELECT', 'TRIG_MODE', 'TRIG_PATTERN', 'SEQUENCE'] + \
    ['C%i:COUPLING' % i for i in range(1,5)] + \
    ['C%i:VOLT_DIV' % i for i in range(1,5)] + \
    ['C%i:OFFSET' % i for i in range(1,5)] + \
    ['C%i:TRIG_COUPLING' % i for i in range(1,5)] + \
    ['C%i:TRIG_LEVEL' % i for i in range(1,5)] + \
    ['C%i:TRIG_SLOPE' % i for i in range(1,5)] + \
    ['C%i:TRACE' % i for i in range(1,5)]

def get_settings(scope):
    settings = {}
    for command in commands:
        scope.send(command + '?')
        settings[command] = scope.recv().strip()
        scope.check_last_command()
    return settings

def set_settings(scope, settings):
    for command, setting in settings.items():
        print('sending %s' % command)
        scope.send(setting)
        scope.check_last_command()

if __name__ == '__main__':
    import sys
    import optparse
    import pickle
    import h5py

    usage = '%prog <save/load> filename'
    parser = optparse.OptionParser(usage)
    options, args = parser.parse_args()

    if len(args) < 2:
        sys.exit(parser.format_help())

    import setup
    from sock import Socket

    scope = Socket(setup.scope_ip, timeout=20.0)
    scope.clear()

    if args[0] == 'save':
        settings = get_settings(scope)
        for command, setting in settings.items():
            print('%s, %s' % (command, setting))
        f = open(args[1], 'wb')
        pickle.dump(settings, f)
        f.close()
    elif args[0] == 'load':
        try:
            f = h5py.File(args[1], 'r')
            settings = dict(f.attrs)
            f.close()
        except h5py.h5e.LowLevelIOError:
            f = open(args[1], 'r')
            settings = pickle.load(f)
            f.close()

        set_settings(scope, settings)
    else:
        raise Exception('unrecognized command %s' % args[0])
