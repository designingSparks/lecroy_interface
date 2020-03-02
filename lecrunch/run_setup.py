"""
This file contains dictionaries for defining attributes to attach to data
files. Each dictionary should contain a 'file' and 'dataset' key whose values
are dictionaries specifying attributes to attach to the root of the hdf5 file
and each dataset in the file respectively. The values in these dictionaries
should contain the type to convert the user's input to before storing them
in the data file.

Example:
    >>> fetch.py test.hdf5 -c default
    /
    /docstring? new batch of pmts
    /channel1
    /channel1.pmtid? trig
    /channel1.voltage? 800
    /channel1.termination? 50.0
    /channel2
    /channel2.pmtid? ZN0103
    /channel2.voltage? 1800.0
    /channel2.termination? 50.0
    ...
    saving event: 1000
    Completed 1000 events in 2.535 seconds.
    Averaged 0.00253 seconds per acquisition.
    Wrote to file 'test.hdf5'.
"""

import string

default = { 'file' : { 'docstring' : str },
            'dataset' : { 'pmtid' : string.lower,
                          'voltage' : float,
                          'termination' : float } }
