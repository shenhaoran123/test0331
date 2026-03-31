EXECUTABLE := 2mm
CUFILES := 2mm.cu

all:
	nvcc -arch=sm_35 -Xptxas -O0 -o ${EXECUTABLE} ${CUFILES}
keep:
	nvcc -arch=sm_35 -Xptxas -O0 -keep -o ${EXECUTABLE} ${CUFILES}

dry:
	nvcc -dryrun -arch=sm_35 -O0 -o ${EXECUTABLE} ${CUFILES} --keep 2>dryrun.out

1noopt:
	nvcc -dryrun -arch=sm_35 -Xcicc -O0 -Xptxas -O0 -o ${EXECUTABLE} ${CUFILES} --keep 2>dryrun.out

noopt:
	nvcc -dryrun -arch=sm_35 -Xptxas -O0 -o ${EXECUTABLE} ${CUFILES} --keep 2>dryrun.out

clean:
	rm -f *.ptx *.ii *.i *.c *.cpp *.gpu *.fatbin *.hash *.o *.cubin *.module_id dryrun.out

clobber:
	rm -f *~ *.ptx *.ii *.i *.c *.cpp *.gpu *.fatbin *.hash *.o *.cubin *.module_id *.out
	rm -rf 2mm result
	rm -f *.txt *.log
