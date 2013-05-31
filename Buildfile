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

justbuild:
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


docs:
	@sh ./makedocs

###############################################################

uninstall: 
	echo  "Uninstall must be done manually!"

.PHONY: install

###############################################################

# useful svn targets
#
#  these are not used, but probably should be...
#

unstable:
	@if [ -e RELEASE ]; then svn mv RELEASE UNSTABLE; fi
	@echo UNSTABLE

stable:
	@if [ -e UNSTABLE ]; then svn mv UNSTABLE RELEASE; fi
	@echo RELEASE

# push and sync to googlecode mirror -- these don't actually
# run the commands, but just tell you what to do..
gpush:
	@echo svnsync init --username mazerj2006 \
		https://pype3.googlecode.com/svn \
		svn+ssh://svn/auto/share/repos/pype3/

gsync:
	@echo svnsync sync --username mazerj2006 https://pype3.googlecode.com/svn
	svnsync sync --username mazerj2006 https://pype3.googlecode.com/svn

