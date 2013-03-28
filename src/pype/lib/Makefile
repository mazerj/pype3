include ../../../make.defs

FILES = *.py

build:
	python ./inline.py *.gif >gificons.py

install: build
	@cp gificons.py $(PYPEDIR)/pype
	@cp cour.ttf testpat.png $(PYPEDIR)/lib


clean:
	@/bin/rm -f im_*.py gificons.py

clobber: clean

