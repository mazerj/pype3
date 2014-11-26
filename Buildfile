include make.defs

SUBDIRS = src

detect:
	@echo "Autodectected version info:"
	@echo " "PYTHONEXE=$(PYTHONEXE)
	@echo " "PYPEDIR=$(PYPEDIR)

setenv:
	@echo "setenv PYTHONEXE $(PYTHONEXE)"
	@echo "setenv PYPEDIR $(PYPEDIR)"

all: install docs clobber

install:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) install);\
		done
	(cd $(PYPEDIR); \
	    $(PYTHONEXE) $(PYCOMPILE) -q pype || $(PYTHONEXE) $(PYCOMPILE) pype)

_reinstall:
	/bin/rm -rf $(PYPEDIR)/pype $(PYPEDIR)/lib

reinstall: _reinstall install

uninstall:
	/bin/rm -rf $(PYPEDIR)

buildonly:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) build);\
		done
	(cd $(PYPEDIR); \
	    $(PYTHONEXE) $(PYCOMPILE) -q pype || $(PYTHONEXE) $(PYCOMPILE) pype)

p2m:
	(cd src; $(MAKE) install-p2m)

pycompile:
	(cd $(PYPEDIR); \
	    $(PYTHONEXE) $(PYCOMPILE) -q pype || $(PYTHONEXE) $(PYCOMPILE) pype)

clobber: 
	@echo "Finding temp files for deletion..."
	@find . -name core -o -name music.raw -o -name \*.pyc | xargs rm -f
	@echo "Cleaning in SUBDIRS..."
	@for i in $(SUBDIRS); \
		do (cd $$i ; echo ...Cleaning $$i ; $(MAKE) clean);\
		done

# makedocs requires epydoc (should probably switch to sphinx...)
docs:
	@sh ./makedocs

################################################################
# push to github ('origin')

push:
	git push

