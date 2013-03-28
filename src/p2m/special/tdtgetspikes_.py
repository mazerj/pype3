#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
#
# Simple wrapper for tdtspike.Spike class to retreive spike
# timestamps and sortcodes from tdt datatank using network api
# into ascii dump file (really for p2mTDTMerge)
#

import sys, posixpath
import pype, tdtspikes, ttank

if __name__ == '__main__':
    from optparse import OptionParser
    
    p = OptionParser('usage: %prog [server/tank/block or pypefile]')
    p.add_option('-s', '--server', dest='server',
                 action='store', type='string', default=None,
                 help='tdt server computer')
    p.add_option('-t', '--tank', dest='tank',
                 action='store', type='string', default=None,
                 help='tdt data tank')
    p.add_option('-b', '--block', dest='block',
                 action='store', type='string', default=None,
                 help='tdt block name')
    p.add_option('-i', '--info', dest='info',
                 action='store_true', default=0,
                 help='info about available channels')

    (options, args) = p.parse_args()

    try:
        if len(args) > 0:
            # user specified a pype data file
            d = tdtspikes.Spikes(pypefile=args[0])
        elif options.server and options.tank and options.block:
            d = tdtspikes.Spikes(server=options.server,
                                 tank=options.tank,
                                 block=options.block)
        else:
            sys.stderr.write("%s: extract from where??\n" % \
                             posixpath.basename(sys.argv[0]))
            sys.exit(1)
        if options.info:
            d.info(sys.stdout)
        else:
            d.dump(sys.stdout)
    except ttank.TDTError:
        sys.stderr.write("%s: can\'t connect to TTank\n" % \
                         posixpath.basename(sys.argv[0]))
        sys.exit(1)
