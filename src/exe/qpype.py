#!/usr/bin/env python
#
# simple tool to quiet python internal network server
#

import asyncore, socket, sys

class Client(asyncore.dispatcher_with_send):
    def __init__(self, host, port, message):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.out_buffer = message

    def handle_close(self):
        self.close()

    def handle_error(self):
        sys.stderr.write('%s not responding.\n' % HOST)
        sys.exit(1)

    def handle_read(self):
        sys.stdout.write(self.recv(1024))
        self.close()

if __name__ == '__main__':
    PORT=5666
    if len(sys.argv) > 2:
        HOST=sys.argv[1]
        CMD=sys.argv[2]
    elif len(sys.argv) > 1:
        HOST='localhost'
        CMD=sys.argv[1]
    else:
        sys.stderr.write('usage: qpype [hostname] cmd\n')
        sys.exit(1)

    c = Client(HOST, PORT, CMD)
    asyncore.loop()
