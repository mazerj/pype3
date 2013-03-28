# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""TDT 'Tank' query tools

Module lets you Retrieve spike timestamps from tdt datatank using
the ttank.py network API.

"""

__author__   = '$Author: mazer $'
__date__     = '$Date: 2010-12-10 11:40:31 -0500 (Fri, 10 Dec 2010) $'
__revision__ = '$Revision: 2 $'
__id__       = '$Id: tdtspikes.py 2 2010-12-10 16:40:31Z mazer $'
__HeadURL__  = '$HeadURL$'

"""Revision History
"""

import sys
import numpy as np
import pypedata, ttank
import time, os, string

from pypedebug import keyboard

class TDTBaseClass:
    """
    Class is intended to open a datatank and query the trial struction
    info, which can later be expanded into spike or LFP data etc..
    """
        
    def __init__(self, rec=None, pypefile=None,
                 server=None, tank=None, block=None):

        # NOTE: Just look at the first pype record (or the
        # user-specified 'rec') to get the necessary tank info. The
        # assumption is that this doesn't change once you start
        # collecting data.

        if rec or pypefile:
            if pypefile:
                pf = pypedata.PypeFile(pypefile)
                rec = pf.nth(0)
                pf.close()
            self.server = rec.params['tdt_server']
            self.tank = rec.params['tdt_tank']
            self.block = rec.params['tdt_block']
        else:
            self.server = server
            self.tank = tank
            self.block = block

        # these environment vars will override the values stored
        # in the datafile:
        if os.environ.has_key('TTANKDIR'):
            # this one should probably have a trailing '\', e.g. 'T:\'
            self.tank = os.envrion['TTANKDIR'] + \
                        string.split(self.tank, '\\')[-1]
        if os.environ.has_key('TTANKSERVER'):
            self.server = os.envrion['TTANKSERVER']

        self.tt = ttank.TTank(self.server)
        if self.tt.invoke('OpenTank', self.tank, 'R'):
            self.tt.invoke('SelectBlock', self.block)
        else:
            sys.stderr.write('Missing tdt tank: %s\n' % self.tank)

        # trl1 is the rising edge of the gating signal
        # this query will get the timestamps for each TRL1 event in SECS
        n = self.tt.invoke('ReadEventsV', 1e6, 'TRL1', 0, 0, 0.0, 0.0, 'ALL')
        trl1 = self.tt.invoke('ParseEvInfoV', 0, n, ttank.TIME)

        # trl2 is the falling edge of the gating signal
        n = self.tt.invoke('ReadEventsV', 1e6, 'TRL2', 0, 0, 0.0, 0.0, 'ALL')
        trl2 = self.tt.invoke('ParseEvInfoV', 0, n, ttank.TIME)

        if len(trl1) != len(trl2):
            # this probably means a new record came in between requesting
            # trl1 and trl2, so truncate the data to only look at complete
            # trials
            sys.stderr.write('Warning: incomplete trial in tdt tank.\n')
            trl1 = trl1[0:len(trl2)]

        self.trl1 = trl1
        self.trl2 = trl2

class Spikes(TDTBaseClass):
    # get all spikes at once, then sort into trials locally..
    # this is much faster -- seems about 1-2 secs to get all the
    # spikes, even for big datasets. Danger is if there's more than
    # 1e6 spikes...
    
    def query(self, chan=0, unit=0, getwaves=None):
        tt = self.tt
        
        if getwaves:
            # pull down the analog snipet waveform data: still needs
            # to be massaged to adjust timestmps..
            nsnip = tt.invoke('ReadEventsV', 1e6, 'Snip', 0, 0, 0.0, 0.0, 'ALL')
            self.waves = tt.invoke('ParseEvV', 0, nsnip)
            self.channel = tt.invoke('ParseEvInfoV', 0, nsnip, ttank.CHANNUM)
            self.sortnum = tt.invoke('ParseEvInfoV', 0, nsnip, ttank.SORTNUM)
            self.ts = tt.invoke('ParseEvInfoV', 0, nsnip, ttank.TIME)

        start, stop = self.trl1[0], self.trl2[-1]
        # get number of spike/snip's between start and stop
        #   chan=0 for any channel
        #   unit=0 for any unit (aka sortcode)
        n = tt.invoke('ReadEventsV', 1e6, 'Snip', \
                      chan, unit, start, stop, 'ALL')

        # get timestamps, channel (electrode), sortnum (unit) for spikes
        tall = np.array(tt.invoke('ParseEvInfoV', 0, n,  ttank.TIME))
        call = np.array(tt.invoke('ParseEvInfoV', 0, n,  ttank.CHANNUM))
        sall = np.array(tt.invoke('ParseEvInfoV', 0, n,  ttank.SORTNUM))
        
        self.sdata = []
        for k in range(len(self.trl1)):
            mask = np.logical_and(np.greater_equal(tall, self.trl1[k]),
                                  np.less_equal(tall, self.trl2[k]))
            t = (np.compress(mask, tall) - self.trl1[k]) * 1000.0
            c = np.compress(mask, call)
            s = np.compress(mask, sall)
            sigs = []
            for j in range(len(s)):
                sigs.append('%03d%c' % (c[j], chr(int(s[j])+ord('a')-1),))
            self.sdata.append((t, c, s, sigs,))
            
        self.ntrials = len(self.trl1)

    def dump(self, out):
        #out.write('#tnum time chan unit\n')
        for k in range(self.ntrials):
            (t, c, s, sigs) = self.sdata[k]
            for j in range(len(t)):
                out.write('%d\t%.1f\t%.0f\t%.0f\n' % (k, t[j], c[j], s[j],))
                #out.write('%d\t%.1f\t%s\n' % (k, t[j], int(c[j]), sigs[j].))

    def info(self, out):
        out.write('server=%s\n' % self.server)
        out.write('tank=%s\n' % self.tank)
        out.write('block=%s\n' % self.block)
        out.write('channels with spikes:\n')
        units = {}
        for k in range(self.ntrials):
            (t, c, s, sigs) = self.sdata[k]
            for j in range(len(t)):
                if s[j]:
                    units[sigs[j]] = 1
        k = units.keys()
        k.sort()
        for sig in k:
            out.write(' %s\n' % sig)

class Raw(TDTBaseClass):
    def query(self, tnum, chan=0):
        # 0 for all channels!
        tt = self.tt
        
        start, stop = self.trl1[tnum], self.trl2[tnum]
        tt.invoke('SetGlobalB', 'Channel', chan)
        tt.invoke('SetGlobalB', 'T1', start)
        tt.invoke('SetGlobalB', 'T2', stop)
        keyboard()
        print start, stop, stop-stop, 's'
        w = np.array(tt.invoke('ReadWavesV', 'RAW0'))
        dt = float(stop-start)/float(w.shape[0])
        t = np.arange(start, stop, step=dt)
        return t, w

    def dump(self, out, dump=0):
        # written trial num and channel num are 1-based
        #out.write('#tnum time chan unit\n')
        for tnum in range(len(self.trl1)):
            sys.stderr.write('retrieving trial %d\n' % tnum)
            tic = time.time()
            t, w = self.query(tnum, chan=0)
            toc = time.time()-tic
            if dump:
                for k in range(w.shape[1]):
                    for j in range(w.shape[0]):
                        out.write('%d\t%f\t%d\t%f\n' % \
                                  (tnum+1, t[j]-t[0], k+1, w[j,k]))
            sys.stderr.write('%d samples/sec\n' % (w.shape[0]*w.shape[1]/toc))

if __name__ == '__main__':
    f = '/auto/data/critters/flea/2008/2008-02-08/flea0137.spotmap.005.gz'
    x = Raw(pypefile=f)
    x.dump(sys.stdout)
    
    sys.stderr.write('%s should never be loaded as main.\n' % __file__)
    sys.exit(1)
