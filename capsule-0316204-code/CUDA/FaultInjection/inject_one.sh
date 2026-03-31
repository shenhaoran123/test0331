output_file="out.txt"
golden_file="golden"
source_file="2mm.cu"
executable_file="2mm"
executable_dry="dryrun1.out"
ptx_file="2mm.ptx"
back_file="2mm1.ptx"
dry_file="dryrun.out"
stdout_file="golden_stdout.txt"
stderr_file="golden_stderr.txt"
result_dir="result"

# compile all
make all

# Standard output directory
if [ ! -d "$golden_file" ];then
    printf "===== Create golden dir =====\n"
    mkdir golden
else
    printf "=====Golden output file have existed=====\n"
fi

# Create golden_stdout.txt and golden_stderr.txt
printf "===== Create golden_stdout.txt and golden_stderr.txt =====\n"
./$executable_file >golden_stdout.txt 2>golden_stderr.txt

# if golden_stdout.txt and golden_stderr.txt in current directory
if [ -f "$stdout_file" ]&&[ -f "$stderr_file" ];then
    mv -f golden_stdout.txt golden/golden_stdout.txt
    mv -f golden_stderr.txt golden/golden_stderr.txt
    printf "===== golden_stdout.txt and golden_stderr.txt move to golden =====\n"
else
    printf "=====golden_stdout.txt or golden_stderr.txt don't exist=====\n"
fi

# Run correctly
./$executable_file
printf "===== Run application correctly =====\n"

# if there are any output files in the current directory
if [ -f "$output_file" ];then
    mv -f out.txt golden/out.txt
    printf "===== out.txt Move to golden =====\n"
else
    printf "===== No output file ====\n"
fi

make clobber

# Modify the compile file
make keep
make dry

# Before Injection
python common_function.py
printf "delete_line back_ptx read_ptx"



if [ ! -d "$result_dir" ];then
    mkdir $result_dir
    printf "===== result created ====\n"
else
    printf "===== result file have exited ====\n"
fi

# Set times of injection
# inject_num=5
middle="_midfile"
for i in $(seq 1 100)
do
    printf "**********************************************THE $i INJECTION*****************************************\n"

    #inject one fault
    python fault-inject.py $i;
    file_name=$i$middle
    cp $ptx_file $result_dir/$file_name
  # if dryrun1.out executable
    if test -x $executable_dry ; then
        ./$executable_dry
        OP_MODE=$?
    else
        printf "===== Increase executable of dryrun1.out =====\n"
        chmod +x $executable_dry
        ./$executable_dry
        OP_MODE=$?
    fi

    # Create sdtout.txt and stderr.txt
    printf "===== Create sdtout.txt and stderr.txt =====\n"
    ./$executable_file 1>stdout.txt 2>stderr.txt

    printf "===== Create out.txt =====\n"
    ./$executable_file

    printf "===== Create diff.log =====\n"
    diff out.txt golden/out.txt>diff.log

    # after injection
    python parse_difference.py $OP_MODE $i
done
