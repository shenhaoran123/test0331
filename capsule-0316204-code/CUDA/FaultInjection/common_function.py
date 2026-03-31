# -*- coding: utf-8 -*-

"""
-- Common Functions (CF)
   CF - V1.0 - July 31, 2023
   Nan Jiang
   College of Computer Science and Technology, Jilin University
"""

ptx_file = "2mm.ptx"
dryrun_before = "dryrun.out"
dryrun_file = "dryrun1.out"  # compile from ptxas
back_file = "2mm1.ptx"
temp_file = "temp.ptx"


"""
- Delete extra lines in dryrun.out
- Output: Executable file dryrun1.out (compile from ptxas)
"""

def delete_line():
    f1 = open(dryrun_before, 'r')
    f2 = open(dryrun_file, 'w')

    i = 0
    for line in f1.readlines():
        if i < 20:
            i += 1
            continue
        i += 1
        line1 = line.strip('#$ ')
        f2.write(line1)
    f1.close()
    f2.close()


# 备份ptx文件

"""
- Backup PTX file
- Output: Backup of PTX file
"""

def back_ptx():
    f1 = open(ptx_file, 'r')
    f2 = open(back_file, 'w')

    for line in f1.readlines():
        f2.write(line)

    f1.close()
    f2.close()

"""
- Generate temp PTX 
- Output: Temp PTX file (temp.ptx)
"""

def read_ptx():
    line_num = 0
    f1 = open(back_file, 'r')
    f2 = open(temp_file, 'w')

    for line in f1.readlines():
        line_num += 1

        analyze_line = line.strip()

        if analyze_line.startswith('// .globl'):
            f2.write(str(line_num) + " ")
            kernel_name = analyze_line.split()[-1]
            f2.write(kernel_name + "\n")
        if analyze_line == "":
            continue
        if analyze_line.startswith('//'):
            continue
        if analyze_line.startswith('.'):
            continue
        if analyze_line.startswith('(') or analyze_line.startswith(')'):
            continue
        if analyze_line.startswith('}') or analyze_line.startswith('{'):
            continue
        if analyze_line.startswith('@'):
            continue
        if analyze_line.startswith('ret'):
            continue

        if analyze_line.startswith('bra'):
            continue
        else:
            f2.write(str(line_num))
            f2.write(" " + analyze_line + "\n")
    f1.close()
    f2.close()


def main():
    # 1 make keep and 2 make dry
    # 3 delete extra line of dryrun.out
    delete_line()
    print("Create dryrun1.out")
    # 4 Backup
    back_ptx()
    print("Backup ptx file")
    # 5 Generate temp.ptx
    read_ptx()
    print("Create temp.txt")


if __name__ == "__main__":
    main()
