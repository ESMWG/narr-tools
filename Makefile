F90 = gfortran-4.9
F90FLAGS =
LDFLAGS = -L/Volumes/Works/soft/lib
LIBS = -lw3

OBJS = fill_dswrf_narr.o
EXE = fill_dswrf_narr.exe

.SUFFIXES:
.SUFFIXES: .o .f90

%.o : %.f90
	$(F90) -c $< -o $@ $(F90FLAGS) 

$(EXE) : $(OBJS)
	$(F90) -o $(EXE) $< $(LDFLAGS) $(LIBS)

fill_dswrf_narr.o : fill_dswrf_narr.f90

.PHONY: clean

clean:
	-rm -f $(OBJS)

distclean: clean
	-rm -f $(EXE)

