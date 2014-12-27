#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

# NOTE: THIS NEEDS THE >= 1.0 pyusb library (not the old c-based version)

VENDOR_ID  = 0x0765
PRODUCT_ID = 0xD094
BUFSIZE    = 8*16
TIMEOUT    = 20000

import sys, string

class OptixMissingDevice(Exception): pass

class Optix():
    def __init__(self):
        import usb.core
        import usb.util
        self.dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if self.dev is None:
            raise OptixMissing
        
        self.dev.set_configuration()
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0,0)]
        self.ep_r = usb.util.find_descriptor(intf,
                            custom_match = \
                            lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        self.ep_w = usb.util.find_descriptor(intf,
                            custom_match = \
                            lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        self.dev.set_interface_altsetting(intf.bInterfaceNumber, intf.bAlternateSetting)

        # will generate error if not attached and set's extra digit precision
        # at same time
        self.reset()
        self.reset()
        self.read('010ACF')               # extra digit resolutio
        self.read('0019CF')               # no black point subtraction
        self.read('ECF')                  # factory cal
        self.read('0117CF')               # enable drift compensation

    def read(self, cmd):
        self.ep_r.clear_halt()
        self.ep_w.clear_halt()
        self.dev.write(self.ep_w.bEndpointAddress, cmd+'\r', TIMEOUT)
        return self.dev.read(self.ep_r.bEndpointAddress, BUFSIZE, TIMEOUT)

    def reset(self):
        self.readstr('0PR')

    def id(self):
        s = self.readstr('SV')
        return s.split('\r')[0]

    def readstr(self, cmd):
        # is is a string of form ..results...\r<NN>, where NN is result code..
        s = string.join(map(chr, self.read(cmd)), '')
        return s
        
    def XYZ(self):
        s = self.readstr('0201RM')
        s = string.strip(string.split(s, '\r')[0])
        return map(float,string.split(s)[1::2])
    
    def Yxy(self):
        s = self.readstr('0301RM')
        s = string.strip(string.split(s, '\r')[0])
        return map(float,string.split(s)[1::2])

    def set_mode(self, lcd=1):
        if lcd:
            self.read('0216CF')
        else:
            self.read('0116CF')

    def selfcalibrate(self):
        self.read('CO')
        
    def clear(self):
        self.read('CE')
        self.read('CE')
        self.read('CE')

if __name__ == '__main__':
    o = Optix()
    o.clear()
    print o.id()
    print 'Yxy', o.Yxy()
    print 'XYZ', o.XYZ()
