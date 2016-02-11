include ../../make.defs

all: clean install

install: exe
	@sh ./install-scripts $(PYPEDIR) *.sh
	@sudo -p"sudo [exe]:" cp -f pype pypenv $(PYPEDIR)/bin
	@sudo -p"sudo [exe]:" cp -f qpype.py $(PYPEDIR)/bin/qpype
ifeq ($(UNAME), Linux)
	@echo "Using sudo to chmod/chown pype"
	@sudo -p"sudo [exe]:" chown root $(PYPEDIR)/bin/pype
	@sudo -p"sudo [exe]:" chmod 4111 $(PYPEDIR)/bin/pype
endif

exe: pypebase.c
	$(CC) -DRUN=\"$(PYPEDIR)/bin/pyperun\" \
	      -DPYTHONEXE=\"$(PYTHONEXE)\" -DPYPE pypebase.c -o pype
	$(CC) -DRUN=\"$(PYPEDIR)/bin/pyperun\" \
	      -DPYTHONEXE=\"$(PYTHONEXE)\" pypebase.c -o pypenv

clean:
	@/bin/rm -f *.o pype pypenv \#*~ .*~
