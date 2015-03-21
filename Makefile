F90 = gfortran-4.9
F90FLAGS =
LDFLAGS = -L/Volumes/Works/soft/lib
LIBS = -lw3

OBJS = filldswrf4ldas_narr.o
EXE = filldswrf4ldas_narr.exe

.SUFFIXES:
.SUFFIXES: .o .f90

%.o : %.f90
	$(F90) -c $< -o $@ $(F90FLAGS) 

$(EXE) : $(OBJS)
	$(F90) -o $(EXE) $< $(LDFLAGS) $(LIBS)

fill_dswrf_narr.o : filldswrf4ldas_narr.f90

.PHONY: clean

clean:
	-rm -f $(OBJS)

distclean: clean
	-rm -f $(EXE)

