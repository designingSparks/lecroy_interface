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
import sys
import numpy as np
import h5py
from ROOT import *
gROOT.SetStyle('Plain')

import optparse
parser = optparse.OptionParser('%prog file')
parser.add_option('-n', type='int', dest='events', default=500)
options, args = parser.parse_args()

f = h5py.File(sys.argv[1], 'r')

mg = {}
for dataset in [f[name] for name in f]:
    mg[dataset.name] = TMultiGraph()

    samples = dataset.attrs['wave_array_count']//dataset.attrs['nom_subarray_count']
    dx = dataset.attrs['horiz_interval']
    dy = dataset.attrs['vertical_gain']
    xoffset = dataset.attrs['horiz_offset']
    yoffset = dataset.attrs['vertical_offset']

    x = np.linspace(xoffset, xoffset + dx*samples, samples)

    for i, waveform in enumerate(dataset[:min(options.events, len(dataset))]):
        print '\rreading waveform: %i' % (i+1),
        sys.stdout.flush()

        y = waveform.astype(np.float64)*dy - yoffset

        mg[dataset.name].Add(TGraph(len(x), x, y))
    print

c = TCanvas('c', '', 800, 600)
c.Divide(1, len(mg))
for i, key in enumerate(mg):
    c.cd(i+1)
    mg[key].SetTitle(';Time (s);Amplitude (V)')
    mg[key].Draw('AL')
    c.cd(i+1).Update()

raw_input('press enter')
