include ../../make.defs

all: clean install

install: exe
	@sh ./install-scripts $(PYPEDIR) *.sh
	@sudo cp -f pype pypenv $(PYPEDIR)/bin
	@echo "Using sudo to chmod/chown pype"
	@sudo chown root $(PYPEDIR)/bin/pype
	@sudo chmod 4111 $(PYPEDIR)/bin/pype

exe: pypebase.c
	$(CC) -DRUN=\"$(PYPEDIR)/bin/pyperun\" \
	      -DPYTHONEXE=\"$(PYTHONEXE)\" -DPYPE pypebase.c -o pype
	$(CC) -DRUN=\"$(PYPEDIR)/bin/pyperun\" \
	      -DPYTHONEXE=\"$(PYTHONEXE)\" pypebase.c -o pypenv

clean:
	@/bin/rm -f *.o pype pypenv \#*~ .*~
