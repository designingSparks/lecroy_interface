#!/usr/bin/env python
import h5py
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle, islice

def roundrobin(*iterables):
    pending = len(iterables)
    nexts = cycle(iter(it).next for it in iterables)

    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

def draw(filename, nevents):
    f = h5py.File(filename, 'r')

    fig = plt.figure()
    for i, dataset in enumerate((f[name] for name in f)):
        plt.subplot(len(f), 1, i+1)
        nevents = min(options.nevents, len(dataset))
        nsamples = dataset.attrs['wave_array_count']//dataset.attrs['nom_subarray_count']
        dx = dataset.attrs['horiz_interval']
        dy = dataset.attrs['vertical_gain']
        xoffset = dataset.attrs['horiz_offset']
        yoffset = dataset.attrs['vertical_offset']

        x = np.tile(np.linspace(xoffset, xoffset+dx*nsamples, nsamples)*1e9, (nevents,1))
        y = dataset[:nevents]*dy - yoffset

        plt.plot(*roundrobin(x, y), color='black')
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (V)')
        plt.title(dataset.name)

    f.close()

    return fig

if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('%prog file [...]')
    parser.add_option('-n', type='int', dest='nevents', default=100)
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit(parser.format_help())

    figures = []
    for filename in args:
        figures.append(draw(filename, options.nevents))

    plt.show()
