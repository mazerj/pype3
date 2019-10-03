include ../make.defs

DACQDIR = dacq4
PYDIR   = pype
SUBDIRS = exe p2m

ifeq ($(UNAME), Linux)
  INSTALL-DACQ=install-dacq
  BUILD-DACQ=build-dacq
else
  INSTALL-DACQ=
  BUILD-DACQ=
endif

install: install-subdirs install-py $(INSTALL-DACQ)

install-shared: install-subdirs install-py-shared

install-subdirs:
	@mkdir -p $(PYPEDIR)
	@mkdir -p $(PYPEDIR)/bin
	@mkdir -p $(PYPEDIR)/pype
	@mkdir -p $(PYPEDIR)/lib
	@mkdir -p $(PYPEDIR)/p2m
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) install);\
		done
	@rm -rf $(PYPEDIR)/pype/Pmw*
	@sh Pmw2/pmw.sh $(PYPEDIR)/pype $(PYTHONEXE)

install-p2m:
	(cd p2m ; $(MAKE) install)


install-py:
	@(cd $(PYDIR); $(MAKE) install)

install-py-shared:
	@(cd $(PYDIR); $(MAKE) install-shared)

install-dacq:
	@(cd $(DACQDIR); $(MAKE) install)

install-dummydacq:
	@(cd $(DUMMYDIR); $(MAKE) install)

build: $(BUILD-DACQ) build-subdirs

build-subdirs:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE));\
		done

build-dacq:
	@(cd $(DACQDIR); $(MAKE))

clean:
	@for i in $(DACQDIR) $(DUMMYDIR) $(SUBDIRS) $(PYDIR); \
		do (cd $$i ; $(MAKE) clean);\
		done

tags:
	rm -f TAGS */TAGS
	etags `pwd`/*/*.{c,h,py}
	for i in $(DACQDIR) $(DUMMYDIR) $(SUBDIRS); \
		do (cd $$i ; ln -s ../TAGS TAGS);\
		done
