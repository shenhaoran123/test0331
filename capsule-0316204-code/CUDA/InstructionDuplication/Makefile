EXECUTABLE := 2mm
CUFILES := 2mm.cu

all:
	nvcc -arch=sm_35 -Xptxas -O0 -keep -o ${EXECUTABLE} ${CUFILES}
dryrun:
	nvcc -dryrun -arch=sm_35 -Xcicc -O0 -Xptxas -O0 -o ${EXECUTABLE} ${CUFILES} --keep 2>dryrun.out

clean:
	rm -f *~ ${EXECUTABLE} *.ii *.i *.gpu *.fatbin *.hash *.o *.cubin *.module_id *.exe *.c *.cpp
	rm -f 2mm1 2mm_dup 2mm_dup_without_load
