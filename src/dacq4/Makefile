include ../../make.defs

#DEBUG = -DDEBUG=1
#DEBUG = -DDEBUG=0

CFLAGS = -O6 -g -Wall $(GLOBAL_CFLAGS) -I$(PYTHONINC) $(DEBUG) -fPIC
COMEDI_SERVER_OBJS = sigs.o psems.o usbjs.o

CC = gcc

all: build install

build: _dacq.so comedi_server

sigs.o: sigs.c sigs.h
	$(CC) $(CFLAGS) -c sigs.c

psems.o: psems.c psems.h
	$(CC) $(CFLAGS) -c psems.c

usbjs.o: usbjs.c usbjs.h
	$(CC) $(CFLAGS) -c usbjs.c

comedi_server.o: comedi_server.c

comedi_server: comedi_server.o $(COMEDI_SERVER_OBJS)
	$(CC) -o $@ $< $(COMEDI_SERVER_OBJS) \
		-lpthread -lcomedi -lm -lrt -lezV24 -leyelink_core

dacq.c: dacq.h

dacq.i: dacq.c dacq.h dacq.i.pre
	@cat dacq.i.pre dacq.h >dacq.i
	@echo "Made dacq.i"

# build extension module using disttools -- the recommended way!
_dacq.so: dacq.i
	swig -python dacq.i
	python setup.py build_ext --inplace

install: _dacq.so comedi_server
	cp dacq.py $(PYPEDIR)/pype
	cp _dacq.so $(PYPEDIR)/pype
	if [ -x comedi_server ]; then cp comedi_server $(PYPEDIR)/bin; fi;

iscandump: iscandump.c
	cc -o iscandump iscandump.c -lezV24


#############################################################


clean:
	@rm -f *.o dacq.py comedi_server _dacq.so *.i *.pyc *_wrap.* .*~ 
	@rm -rf build

