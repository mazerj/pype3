include ../../make.defs

P2MDIR = $(PYPEDIR)/p2m

install:
	mkdir -p $(P2MDIR)
	sh ./install-scripts $(P2MDIR)
	/bin/cp -f README *.m $(P2MDIR)
	@date > $(P2MDIR)/LAST_UPDATE

build:
	@echo "p2m: Nothing to build."

tags:
	@echo "p2m: nothing to tagify."

clean:
	/bin/rm -f \#*~
