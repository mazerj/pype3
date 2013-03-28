OBJS = main.o  targets.o  trial.o  trials.o
EYELINK_LIB=../../../lib
EYELINK_INCLUDE=../../../include
LINKLIBS=-L$(EYELINK_LIB) -leyelink_core -leyelink_core_graphics  -lsdl_util `sdl-config --libs`  -lgd
CFLAGS=-I$(EYELINK_INCLUDE) `sdl-config --cflags`
dynamic: $(OBJS)
	$(CC) -o dynamic $(OBJS) $(LINKLIBS)
clean:
	-rm -rf $(OBJS) dynamic
