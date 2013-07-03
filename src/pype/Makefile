include ../../make.defs

install:  mklib mkpyperun mkpypeversion mkinit 
	@cp *.py $(PYPEDIR)/pype
	@cp pypespike.sh $(PYPEDIR)/bin/pypespike
	@chmod +x $(PYPEDIR)/bin/pypespike
	@rm -f pypeversion.py
	@rm -f __init__.py

# clean out vestigal .py files etc to make sure old stuff gets
# deleted
preinstallclean_:
	@/bin/rm -rf $(PYPEDIR)/pype/*

mkinit:
	@sh mkinit.sh >__init__.py

mkpypeversion:
	@sh mkpypeversion.sh >pypeversion.py

mkpyperun:
	@cp pyperun $(PYPEDIR)/bin
	@chmod +x $(PYPEDIR)/bin/pyperun

mklib:
	@(cd ./lib ; $(MAKE) install)

tags:
	etags *.py

build:
	@echo "nothing to do in `pwd` for build"

clean:
	(cd ./lib ; $(MAKE) clean)
	@rm -f *.pyc .*~ prun __init__.py pypeversion.py

