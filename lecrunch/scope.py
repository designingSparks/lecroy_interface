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

import struct
import socket
import os

headerformat = '>BBBBL'

errors = { 1 : 'unrecognized command/query header',
           2 : 'illegal header path',
           3 : 'illegal number',
           4 : 'illegal number suffix',
           5 : 'unrecognized keyword',
           6 : 'string error',
           7 : 'GET embedded in another message',
           10 : 'arbitrary data block expected',
           11 : 'non-digit character in byte count field of ' \
                'arbitrary data block',
           12 : 'EOI detected during definite length data block transfer',
           13 : 'extra bytes detected during definite length data block ' \
                'transfer' }

class Scope(object):
    """
    A class for low level communication with the oscilliscope over a socket
    connection.
    """
    def __init__(self, host, port=1861, timeout=2.0):
        """Create a socket object to *host* over *port*"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.host = host
        self.port = port
        self.timeout = timeout

    def settimeout(self, timeout):
        """Set the *timeout* for the socket connection in seconds."""
        self.sock.settimeout(timeout)
        self.timeout = timeout
        
    def connect(self):
        """Make the socket connection."""
        self.sock.connect((self.host, self.port))

    def clear(self):
        """Clear the oscilloscope's output queue."""
        self.sock.settimeout(2.0)
        try:
            while True:
                self.sock.recv(100)
        except socket.timeout:
            pass
        self.sock.settimeout(self.timeout)

    def close(self):
        """Close the socket connection."""
        self.sock.close()

    def send(self, str):
        """Format and send the string *str*."""
        if not str.endswith('\n'):
            str += '\n'
        header = struct.pack(headerformat, 129, 1, 1, 0, len(str))
        self.sock.sendall(header + str)

    def check_last_command(self):
        """
        Check that the last command sent was received okay; if not, then
        raise an exception with details about the error.
        """
        self.send('cmr?')
        err = int(self.recv().split(' ')[-1].rstrip('\n'))

        if err in errors:
            self.close()
            raise Exception(errors[err])

    def getheader(self):
        """
        Unpacks a header string from the oscilloscope into the tuple
        (operation, header version, sequence number, spare, total bytes).
        """
        return struct.unpack(headerformat, self.sock.recv(8))

    def recv(self):
        """
        Receive, concatenate, and return a 'logical series' of blocks from
        the oscilloscope. A 'logical series' consists of one or more blocks
        in which the final block is terminated by an EOI terminator
        (i.e. the EOI bit in the header block is set to '1').
        """
        reply = ''
        while True:
            operation, headerver, seqnum, spare, totalbytes  = self.getheader()

            buffer = ''

            while len(buffer) < totalbytes:
                buffer += self.sock.recv(totalbytes - len(buffer))

            reply += buffer

            if operation % 2:
                break
            
        return reply

if __name__ == '__main__':
    import sys
    import setup

    scope = Scope(setup.scope_ip)
    scope.connect()
    scope.clear()

    for msg in sys.argv[1:]:
        scope.send(msg)
        if '?' in msg:
            print repr(scope.recv())

        scope.check_last_command()

    scope.close()
