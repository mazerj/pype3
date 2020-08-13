# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
import threading
import socket
import string
import time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from pype import getapp
#from guitools import Logger

class PypeHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		
		cmd = self.path
		#print 'cmd: <%s>' % cmd
		
		if cmd == '/':
			h = socket.gethostname().split('.')[0]
			s = string.replace(getapp().last_tally, '\n', '<br>\n')
			self.wfile.write("""<META HTTP-EQUIV="refresh" CONTENT="5">\n""")
			self.wfile.write("""<style>h1,h2 { font-family: sans-serif; }</style>\n""")
			self.wfile.write("""<h1>pype on %s</h1>\n""" % (h,))
			self.wfile.write("""<h2>%s</h1>\n""" % (time.strftime('%c'),))
			self.wfile.write("""<hr>\n""")
			if getapp().running:
				self.wfile.write("""RUNNING: %s<br>\n""" % getapp().task_name)
			else:
				self.wfile.write("""IDLE<br>\n""")
			self.wfile.write("""<hr>\n""")
			self.wfile.write("""<tt>\n%s</tt>\n""" % s)
		else:
			self.wfile.write('Unknown command: %s\n' % cmd);
		return

	def log_message(self, format, *args):
		# stop logging to stdout
		return

class PypeHTTPServer():
	def __init__(self, app):
		self.app = app
		self.server = None

	def start(self):
		self.server = HTTPServer(('', self.app.config.iget('HTTP_PORT')),
								 PypeHandler)
		self.server_thread = threading.Thread(target=self.non_int_serve_forever)
		self.server_thread.daemon = True
		self.server_thread.start()
		#Logger('http: started server at http://%s:%d\n' % \
		#		(self.app._gethostname(fqdn=True),
		#		 self.app.config.iget('HTTP_PORT')))

	def shutdown(self):
		self.server.shutdown()

	def non_int_serve_forever(self, poll_interval=0.5):
		# prevent signals (SIGALRM and stuff from comedi_server etc
		# from interupting select call
		while 1:
			try:
				self.server.serve_forever()
				break
			except:
				pass
		


