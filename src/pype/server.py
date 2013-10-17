# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
#
import asyncore, socket, threading

class Server(asyncore.dispatcher):
	def __init__(self, host, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.bind(('', port))
		self.listen(1)

	def handle_accept(self):
		# when we get a client connection start a dispatcher for that
		# client
		socket, address = self.accept()
		print 'Connection by', address
		EchoHandler(socket)

class EchoHandler(asyncore.dispatcher_with_send):
	# dispatcher_with_send extends the basic dispatcher to have an output
	# buffer that it writes whenever there's content
	def handle_read(self):
		self.out_buffer = self.recv(1024)
		if not self.out_buffer:
			self.close()

s = Server('', 5007)
t = threading.Thread(target=asyncore.loop)
t.start()
while threading.active_count > 0:
    pass

