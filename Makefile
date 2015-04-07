F90 = gfortran-4.9
F90FLAGS =
LDFLAGS = -L/Volumes/Works/soft/lib
LIBS = -lw3

OBJS = narr_filldswrf4ldas.o
EXE = narr_filldswrf4ldas.exe

.SUFFIXES:
.SUFFIXES: .o .f90

%.o : %.f90
	$(F90) -c $< -o $@ $(F90FLAGS) 

$(EXE) : $(OBJS)
	$(F90) -o $(EXE) $< $(LDFLAGS) $(LIBS)

narr_filldswrf4ldas.o : narr_filldswrf4ldas.f90

.PHONY: clean

clean:
	-rm -f $(OBJS) $(EXE)

