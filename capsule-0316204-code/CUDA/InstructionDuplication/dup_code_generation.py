# -*- coding: utf-8 -*-

import os, io, sys, re, math, random
import numpy as np

app_name = "2mm"
ptx_file = "temp.ptx"
f_ptx_file = "2mm_dup.ptx"

back_file = "2mm_original.ptx"

"""
- Analyze the target instruction
- Input: Line number of target instruction
- Ouput: ins_str, ins opcode, total op number, des register, des register type, des register id, op list
"""

def analyze_ins(line):
    total_op_num = 0
    split_line = line.split()  # cvta.to.global.u64 	%rd1, %rd8;

    # 1. ins_opcode
    ins_opcode = split_line[0]

    # 2. op number
    if len(split_line) == 3:
        total_op_num = 2
    elif len(split_line) == 4:
        total_op_num = 3
    else:
        total_op_num = 4

    # 3. destination register
    des_reg = split_line[1]

    # 4. destination register type
    des_reg_type = re.sub("[^a-z]", "", split_line[1])
    
    # 5. destination register id
    des_reg_id = re.sub("[^0-9]", "", split_line[1])

    # 6. op list
    op_list = []
    for i in range( 1 , total_op_num + 1 ):
        op_list.append(split_line[i])

    return split_line, ins_opcode, total_op_num, des_reg, des_reg_type, des_reg_id, op_list

"""
- Judge in which kernel
- Input: Line number of target instruction
- Ouput: Kernel id
"""

def in_which_kernel(line):
    if line in range(1,125):
        kernel = '1'
    else:
        kernel = '2'
    return kernel

"""
- Dup PTX generaation (need further modify .reg)
- Ouput: after-dup reg numbern, temp.ptx
"""

def dup_ins():
    line_num = 0
    # obtain from ML and dep graph
    dep_chain1 = [51, 63, 65, 68, 69, 72, 73, 77, 81, 85, 89, 93]
    dep_chain2 = [53, 54, 55, 56]
    dep_chain3 = [142, 155, 156, 160, 164, 168, 172, 176, 180, 184]
    dep_chain4 = [144, 145, 146, 147]

    com_site = {"100":"BB0_3","191":"BB1_3"}

    # app-specific register information 
    # kernel 1
    pred_for_com = 5 
    pred_for_com1 = 6 
    pred_reg_number = 7  # pred number (x+2)
    f_reg_number = 28   # f number
    # r_for_com = 22
    r_reg_number = 22  # r number (x+1)
    rd_reg_number = 16  # rd number
    
    #kernel 2
    pred_for_com2 = 5 
    pred_for_com12 = 6
    pred_reg_number2 = 7  # pred number (x+2)
    f_reg_number2 = 28  # f number
    # r_for_com_2 = 22
    r_reg_number2 = 22  # r number (x+1)
    rd_reg_number2 = 16  # rd number

    
    # original-reg:after-reg --> key:value
    reg_replace = {}

    pfile = open(ptx_file, "w")
    bfile = open(back_file, 'r')

    for line in bfile.readlines():
        line_num += 1

        if in_which_kernel(line_num) == '1':
            if dep_chain1.count(line_num) != 0 or dep_chain2.count(line_num) != 0:
                split_line, ins_opcode, total_op_num, des_reg, des_reg_type, des_reg_id, op_list = analyze_ins(line)
            
                if line_num == dep_chain1[0] or line_num == dep_chain2[0]:

                    # write dup ins
                    if des_reg_type == 'f':
                        new_des_reg = "%" + str(des_reg_type) + str(f_reg_number)
                        f_reg_number += 1
                    elif des_reg_type =='r':
                        new_des_reg = "%" + str(des_reg_type) + str(r_reg_number)
                        r_reg_number += 1
                    elif des_reg_type == 'rd':
                        new_des_reg = "%" + str(des_reg_type) + str(rd_reg_number)
                        rd_reg_number += 1
                    else:
                        new_des_reg = "%" + str(des_reg_type) + str(pred_reg_number)
                        pred_reg_number += 1
                    reg_replace[str(des_reg[0:-1])] = new_des_reg
                    
                    if total_op_num == 2:
                        dup_ins = '       ' + str(ins_opcode) + "  " + str(new_des_reg) + ", " + split_line[-1] + '\n'
                    elif total_op_num == 3:
                        dup_ins = '       ' + str(ins_opcode) + "  " + str(new_des_reg) + ", " \
                                + split_line[-2] + " " + split_line[-1]  + '\n'
                    else:
                        dup_ins = '       ' + str(ins_opcode) + "  " + str(new_des_reg) + ", " \
                                + split_line[-3] + " " + split_line[-2] + " " + split_line[-1]  + '\n'

                    pfile.write(dup_ins)

                    # write original ins
                    pfile.write(line)
                elif str(line_num) in dep_chain1 or dep_chain2:
                    # write dup ins
                    dup_ins = '       ' + str(ins_opcode)

                    # des_reg 
                    if des_reg_type == 'f':
                        new_des_reg = "%" + str(des_reg_type) + str(f_reg_number)
                        f_reg_number += 1
                    elif des_reg_type =='r':
                        new_des_reg = "%" + str(des_reg_type) + str(r_reg_number)
                        r_reg_number += 1
                    elif des_reg_type == 'rd':
                        new_des_reg = "%" + str(des_reg_type) + str(rd_reg_number)
                        rd_reg_number += 1
                    else:
                        new_des_reg = "%" + str(des_reg_type) + str(pred_reg_number)
                        pred_reg_number += 1
                    reg_replace[str(des_reg)] = new_des_reg


                    dup_ins += " " + new_des_reg + ","
                    
                    for i in range(1,total_op_num):
                        if str(op_list[i]) in reg_replace.keys():
                            if i == total_op_num - 1:
                                op_i = reg_replace[str(op_list[i])] + ";"
                            else:
                                op_i = reg_replace[str(op_list[i])] + ","
                        else:
                            op_i = op_list[i]
                        dup_ins += " " + op_i

                    pfile.write(dup_ins + '\n')

                    # write original ins
                    pfile.write(line)


                    if line_num == dep_chain1[-1] or line_num == dep_chain2[-1] or line_num == dep_chain3[-1] or line_num == dep_chain4[-1]:
                        if des_reg_type == 'rd':
                            ins_com1 = "setp.eq.s64 " + "%p" + str(pred_for_com2) + ", " + str(des_reg) + " " \
                                    + str(reg_replace[str(des_reg)]) + ";"
                        else:
                            if des_reg_type == 'f':
                                ins_com1 = "setp.eq." + str(des_reg_type) + "32     " + "%p" + str(pred_for_com2) + ", " + str(des_reg) + " " + str(reg_replace[str(des_reg)]) + ";"
                            else:
                                ins_com1 = "setp.eq.s32     " + "%p" + str(pred_for_com2) + ", " + str(des_reg) + " " \
                                        + str(reg_replace[str(des_reg)]) + ";"
                        
                        if line_num in dep_chain1 or line_num in dep_chain2 or line_num in dep_chain3 or line_num in dep_chain4:
                            ins_com2 = "or.pred     " + "%p" + str(pred_for_com12) + ", " \
                                        + "%p" + str(pred_for_com2) + ", 0;"
                        else:
                            ins_com2 = "or.pred     " + "%p" + str(pred_for_com12) + ", " \
                                        + "%p" + str(pred_for_com12) + ", " + "%p" + str(pred_for_com2) + ";"

                        # ins_com2 = "setp.ne " + "%p" + str(pred_for_com) + ", " + "%r" + str(r_for_com) + ", 0x0;"

                        pfile.write('       ' + ins_com1 + "\n")
                        pfile.write('       ' + ins_com2 + "\n")


                    if line_num == dep_chain1[-1] or line_num == dep_chain2[-1] or line_num == dep_chain3[-1] or line_num == dep_chain4[-1]:
                        if des_reg_type == 'rd':
                            ins_com1 = "setp.eq.s64 " + "%p" + str(pred_for_com) + ", " + str(des_reg) + " " \
                                    + str(reg_replace[str(des_reg)]) + ";"
                        else:
                            if des_reg_type == 'f':
                                ins_com1 = "setp.eq." + str(des_reg_type) + "32     " + "%p" + str(pred_for_com) + ", " + str(des_reg) + " " + str(reg_replace[str(des_reg)]) + ";"
                            else:
                                ins_com1 = "setp.eq.s32     " + "%p" + str(pred_for_com) + ", " + str(des_reg) + " " \
                                        + str(reg_replace[str(des_reg)]) + ";"

                        if line_num in dep_chain1 or line_num in dep_chain2 or line_num in dep_chain3 or line_num in dep_chain4:
                            ins_com2 = "or.pred     " + "%p" + str(pred_for_com1) + ", " \
                                        + "%p" + str(pred_for_com) + ", 0;"
                        else:
                            ins_com2 = "or.pred     " + "%p" + str(pred_for_com1) + ", " \
                                        + "%p" + str(pred_for_com1) + ", " + "%p" + str(pred_for_com) + ";"
                        pfile.write('       ' + ins_com1 + "\n")
                        pfile.write('       ' + ins_com2 + "\n")
                else:
                    # write original ins
                    pfile.write(line + "\n")
            elif str(line_num) in com_site.keys():
                com_ins1 = "@%p" + str(pred_for_com) + " bra " + com_site[str(line_num)] + ";"
                bra_ins = "BB0_100:"
                trap_ins = "    trap;"
                pfile.write('       ' + com_ins1 + "\n")
                pfile.write(bra_ins + "\n")
                pfile.write(trap_ins + "\n")
            else:
                pfile.write(line)
        else:
            if dep_chain1.count(line_num) != 0 or dep_chain2.count(line_num) != 0 or dep_chain3.count(line_num) != 0 or dep_chain4.count(line_num) != 0:
                split_line, ins_opcode, total_op_num, des_reg, des_reg_type, des_reg_id, op_list = analyze_ins(line)
            
                if line_num == dep_chain1[0] or line_num == dep_chain2[0] or line_num == dep_chain3[0] or line_num == dep_chain4[0]:

                    # write dup instruction
                    if des_reg_type == 'f':
                        new_des_reg = "%" + str(des_reg_type) + str(f_reg_number2)
                        f_reg_number2 += 1
                    elif des_reg_type =='r':
                        new_des_reg = "%" + str(des_reg_type) + str(r_reg_number2)
                        r_reg_number2 += 1
                    elif des_reg_type == 'rd':
                        new_des_reg = "%" + str(des_reg_type) + str(rd_reg_number2)
                        rd_reg_number2 += 1
                    else:
                        new_des_reg = "%" + str(des_reg_type) + str(pred_reg_number2)
                        pred_reg_number2 += 1
                    reg_replace[str(des_reg[0:-1])] = new_des_reg
                    
                    if total_op_num == 2:
                        dup_ins = '       ' + str(ins_opcode) + "  " + str(new_des_reg) + ", " + split_line[-1] + '\n'
                    elif total_op_num == 3:
                        dup_ins = '       ' + str(ins_opcode) + "  " + str(new_des_reg) + ", " \
                                + split_line[-2] + " " + split_line[-1]  + '\n'
                    else:
                        dup_ins = '       ' + str(ins_opcode) + "  " + str(new_des_reg) + ", " \
                                + split_line[-3] + " " + split_line[-2] + " " + split_line[-1]  + '\n'

                    pfile.write(dup_ins)

                    # write original instruction
                    pfile.write(line)
                elif str(line_num) in dep_chain1 or dep_chain2 or dep_chain3 or dep_chain4:
                    # write dup instruction
                    dup_ins = '       ' + str(ins_opcode)

                    # des_reg 
                    if des_reg_type == 'f':
                        new_des_reg = "%" + str(des_reg_type) + str(f_reg_number2)
                        f_reg_number2 += 1
                    elif des_reg_type =='r':
                        new_des_reg = "%" + str(des_reg_type) + str(r_reg_number2)
                        r_reg_number2 += 1
                    elif des_reg_type == 'rd':
                        new_des_reg = "%" + str(des_reg_type) + str(rd_reg_number2)
                        rd_reg_number2 += 1
                    else:
                        new_des_reg = "%" + str(des_reg_type) + str(pred_reg_number2)
                        pred_reg_number2 += 1
                    reg_replace[str(des_reg)] = new_des_reg

                    dup_ins += " " + new_des_reg + ","
                    
                    for i in range(1,total_op_num):
                        if str(op_list[i]) in reg_replace.keys():
                            if i == total_op_num - 1:
                                op_i = reg_replace[str(op_list[i])] + ";"
                            else:
                                op_i = reg_replace[str(op_list[i])] + ","
                        else:
                            op_i = op_list[i]
                        dup_ins += " " + op_i

                    pfile.write(dup_ins + '\n')

                    # write original instruction
                    pfile.write(line)
                    
                    if line_num == dep_chain1[-1] or line_num == dep_chain2[-1] or line_num == dep_chain3[-1] or line_num == dep_chain4[-1]:
                        if des_reg_type == 'rd':
                            ins_com1 = "setp.eq.s64 " + "%p" + str(pred_for_com2) + ", " + str(des_reg) + " " \
                                    + str(reg_replace[str(des_reg)]) + ";"
                        else:
                            if des_reg_type == 'f':
                                ins_com1 = "setp.eq." + str(des_reg_type) + "32     " + "%p" + str(pred_for_com2) + ", " + str(des_reg) + " " + str(reg_replace[str(des_reg)]) + ";"
                            else:
                                ins_com1 = "setp.eq.s32     " + "%p" + str(pred_for_com2) + ", " + str(des_reg) + " " \
                                        + str(reg_replace[str(des_reg)]) + ";"
                        
                        if line_num in dep_chain1 or line_num in dep_chain2 or line_num in dep_chain3 or line_num in dep_chain4:
                            ins_com2 = "or.pred     " + "%p" + str(pred_for_com12) + ", " \
                                        + "%p" + str(pred_for_com2) + ", 0;"
                        else:
                            ins_com2 = "or.pred     " + "%p" + str(pred_for_com12) + ", " \
                                        + "%p" + str(pred_for_com12) + ", " + "%p" + str(pred_for_com2) + ";"

                        # ins_com2 = "setp.ne " + "%p" + str(pred_for_com) + ", " + "%r" + str(r_for_com) + ", 0x0;"

                        pfile.write('       ' + ins_com1 + "\n")
                        pfile.write('       ' + ins_com2 + "\n")
                else:
                    # write original instruction
                    pfile.write(line + "\n")
            elif str(line_num) in com_site.keys():
                com_ins1 = "@%p" + str(pred_for_com2) + " bra " + com_site[str(line_num)] + ";"
                bra_ins = "BB1_100:"
                trap_ins = "    trap;"
                pfile.write('       ' + com_ins1 + "\n")
                pfile.write(bra_ins + "\n")
                pfile.write(trap_ins + "\n")
            else:
                pfile.write(line)

    pfile.close()
    bfile.close()

    return pred_reg_number, f_reg_number, r_reg_number, rd_reg_number, pred_reg_number2, f_reg_number2, r_reg_number2, rd_reg_number2

"""
- Modify reg number, generate final PTX
- Input: Reg number
- Ouput: Dup file (2mm.ptx)
"""

def modify_reg(pred_reg_number, f_reg_number, r_reg_number, rd_reg_number, pred_reg_number2, f_reg_number2, r_reg_number2, rd_reg_number2):
    file = open(f_ptx_file, "w")
    tfile = open(ptx_file, "r")
    

    line_num = 0

    for line in tfile.readlines():
        
        line_num += 1
        kernel = in_which_kernel(line_num)
        if kernel == '1':
            if line.strip().startswith('.reg'):
                type_item = line.strip().split()[1]  
                if type_item == ".pred":
                    str_1 = ".reg .pred   %p<" + str(pred_reg_number) + ">;"
                    file.write('    ' + str_1 + '\n')   
                elif type_item == ".f32":
                    str_1 = ".reg .f32   %f<" + str(f_reg_number) + ">;"
                    file.write('    ' + str_1 + '\n') 
                elif type_item == ".b32":
                    str_1 = ".reg .b32   %r<" + str(r_reg_number) + ">;"
                    file.write('    ' + str_1 + '\n') 
                elif type_item == ".b64":
                    str_1 = ".reg .b64   %rd<" + str(rd_reg_number) + ">;"
                    file.write('    ' + str_1 + '\n') 
            else:
                file.write(line) 
        else:
            if line.strip().startswith('.reg'):
                type_item = line.strip().split()[1]  
                if type_item == ".pred":
                    str_1 = ".reg .pred   %p<" + str(pred_reg_number2) + ">;"
                    file.write('    ' + str_1 + '\n')   
                elif type_item == ".f32":
                    str_1 = ".reg .f32   %f<" + str(f_reg_number2) + ">;"
                    file.write('    ' + str_1 + '\n') 
                elif type_item == ".b32":
                    str_1 = ".reg .b32   %r<" + str(r_reg_number2) + ">;"
                    file.write('    ' + str_1 + '\n') 
                elif type_item == ".b64":
                    str_1 = ".reg .b64   %rd<" + str(rd_reg_number2) + ">;"
                    file.write('    ' + str_1 + '\n') 
            else:
                file.write(line) 
    file.close()
         
def main():
    pred_reg_number, f_reg_number, r_reg_number, rd_reg_number, pred_reg_number2, f_reg_number2, r_reg_number2, rd_reg_number2 = dup_ins()
    modify_reg(pred_reg_number, f_reg_number, r_reg_number, rd_reg_number, pred_reg_number2, f_reg_number2, r_reg_number2, rd_reg_number2)

if __name__ == "__main__":
    main()
