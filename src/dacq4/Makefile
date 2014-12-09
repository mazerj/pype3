include ../../make.defs

UNAME := $(shell uname)

# only try to build the the comedi_server under linux..
ifeq ($(UNAME), Linux)
  COMEDI_SERVER = comedi_server
else
  COMEDI_SERVER = dummy_server
endif

CC = gcc
CFLAGS = -O6 -g -Wall $(GLOBAL_CFLAGS) -I$(PYTHONINC) -fPIC
COMEDI_SERVER_OBJS = sigs.o psems.o usbjs.o


all: build install

build: _dacq.so $(COMEDI_SERVER)

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

dummy_server.o: dummy_server.c

dummy_server: dummy_server.o $(COMEDI_SERVER_OBJS)
	$(CC) -o $@ $< $(COMEDI_SERVER_OBJS)

dacq.c: dacq.h

dacq.i: dacq.c dacq.h dacq.i.pre
	@cat dacq.i.pre dacq.h >dacq.i
	@echo "Made dacq.i"

# build extension module using disttools -- the recommended way!
_dacq.so: dacq.i
	@swig -python dacq.i
	@python setup.py build_ext --inplace

install: _dacq.so $(COMEDI_SERVER)
	@cp dacq.py $(PYPEDIR)/pype
	@cp _dacq.so $(PYPEDIR)/pype
	@if [ -x comedi_server ]; then cp comedi_server $(PYPEDIR)/bin/comedi_server; fi;
	@if [ -x dummy_server ]; then cp dummy_server $(PYPEDIR)/bin/comedi_server; fi;

iscandump: iscandump.c
	cc -o iscandump iscandump.c -lezV24


#############################################################


clean:
	@rm -f dacq.py comedi_server dummy_server _dacq.so \
		*.o *.i *.pyc *_wrap.* .*~ 
	@rm -rf build

