# -*- coding: utf-8 -*-


import os, io, sys, re, math, random
import numpy as np


"""
-- Fault Injection (FI)
   FI - V1.0 - July 31, 2023
   Nan Jiang
   College of Computer Science and Technology, Jilin University
"""


app_name = "2mm"
ptx_file = "2mm.ptx"
dryrun_before = "dryrun.out"
# compile from ptxas
dryrun_file = "dryrun1.out"
back_file = "2mm1.ptx"
temp_file = "temp.ptx"
basic_file = "basic.txt"



"""
- Specify or obtain instruction list for FI
- Output: Instruction list for FI
"""

def instruction_list():

    ins_list = []
    start_line = 45
    end_line = 99

    line_number = 0
    f = open(back_file,'r')


    for line in f.readlines():

        line_number += 1
        line.strip()
        # delete space
        analyze_line = line.strip()
        ana_ins = analyze_line.split(' ')

        if analyze_line.startswith('//') or analyze_line.startswith('.') or analyze_line.startswith(')') \
                or analyze_line.startswith('{') or analyze_line.startswith('}') or analyze_line == '' \
                or analyze_line.startswith('BB') or analyze_line.startswith('ret') or analyze_line.startswith('_'):
            continue
        # analyze_line.startswith(bra)
        elif analyze_line.startswith('@') or analyze_line.startswith('bra') or analyze_line[0].split('.')[-1] == 'f32':
            continue
        elif analyze_line.startswith('st'):
            continue
        elif start_line < line_number < end_line :
            if "rd" in analyze_line:
                continue
            else:
                ins_list.append(line_number)
            continue
        else:
            continue
    print(ins_list)
    return ins_list


"""
- Generate random fault value
- Input: Register bits of the destination register of target instruction
- Output: Fault value in hexadecimal, random bit
"""

def random_bit(reg_digit):
    # for pred register
    if reg_digit == 1:
        ran_bit = random.randint(0, 1)
    else:
        ran_bit = random.randint(0, int(reg_digit)-1)  # generate random value
    dec_num = str(int(math.pow(2, ran_bit))).replace(".0", "")  # float to str
    fault_value = hex(np.compat.long(str(dec_num), 10))  # convert to hexadecimal
    fault_value = str(fault_value).strip('L')
    return fault_value, ran_bit


"""
- Choose FI loop depth
- Input: Thread number
- Output: Random loop depth
"""

def random_loop_time(thread_num):

    ran_loop = random.randint(1,thread_num/8)
    return ran_loop

"""
- Judge whether the target instruction is in a loop
- Input: Line number of the target instruction
- Output: Y/N
"""

def in_loop(target_line):

    # adjust
    if 60 < int(target_line) < 101:
        return '1'
    elif 152 < int(target_line) < 193:
        return '1'
    else:
        return '0'

"""
- Specify or randomly choose target instruction for FI
- Input: Instruction list
- Output: Line number of target instruction
"""

def inject_line_num(ins_list):
    target_line = random.choice(ins_list)
    return target_line


"""
- Specify or randomly select thread for FI
- Input: Thread id range
- Output: Thread id for FI
"""

def random_thread2(thread_x, thread_y):
    random_x = random.randint(0, thread_x - 1)
    random_y = random.randint(0, thread_y - 1)
    return random_x, random_y

def random_thread1(thread_x):
    random_x = random.randint(0, thread_x - 1)
    return random_x


"""
- Get label number
- Output: Label number
"""

def get_label():
    f1 = open(back_file, 'r')
    label_num = 0
    for line in f1.readlines():
        if line.startswith('BB0_') or line.startswith('BB1_'):
            label_num += 1
    f1.close()
    return label_num


"""
- Get kernel number
- Output: Kernel number
"""

def get_kernel_info():
    f1 = open(back_file, 'r')
    line_num = 0
    kernel_dict = {}
    kernel_num = 0
    for line in f1.readlines():
        line_num += 1
        analyze_line = line.strip()
        # is kernel name
        if analyze_line.startswith('// .globl'):
            kernel_name = analyze_line.split()[-1]  # kernel name 
            kernel_num += 1
            kernel_dict.update([(kernel_num, kernel_name)])
    return kernel_num, kernel_dict


"""
- Get kernel name and the last param
- Input: Target instruction id, kernel name dict
- Output: Kernel name, last param (only when collecting bit-flip direction, .cu file should modify)
"""

def get_kernel_name_param(target_line, kernel_dict):
    kernel_name = ''
    last_param = ''
    if 15 < int(target_line) < 102:
        kernel_name = kernel_dict.get(1)
        last_param = '[_Z11mm2_kernel1PfS_S_Pd_param_3]'
                       #_Z11mm2_kernel1PfS_S_Pd_param_3
    else:
        kernel_name = kernel_dict.get(2)
        last_param = '[_Z11mm2_kernel2PfS_S_Pd_param_3]'
    return kernel_name, last_param


"""
- Analyze target instruction
- Input: Line number of target instruction
- Output: Instruction opcode, destination register digit (1/32/64), destination register type, destination register (%r11)
"""

def analyze_ins(target_line):
    f = open(temp_file, 'r')
    for line in f.readlines():
        split_line = line.split()
        
        if len(split_line) > 2:

            if split_line[0] == str(target_line):
                ins_str = split_line[1]
                des_str = split_line[2]


                ins_str_list = ins_str.split('.')  # ld.param.u64  mov.u32
                # mov u32
                if len(ins_str_list) == 2:
                    ins_opcode = ins_str_list[0] # mov,mad,ld....
                    reg_str = ins_str_list[-1]  # s32,u32,s64,b32,f32
                    if reg_str == "pred":
                        reg_digit = "1"
                        reg_type = "pred"
                    else:
                        reg_digit = re.sub("[^0-9]", "", reg_str)
                        reg_type = re.sub("[^a-z]", "", reg_str)
                # ld param u64
                else:
                    ins_opcode = ins_str_list[0]  # mov,mad,ld....
                    reg_str = ins_str_list[-1]  # s32,u32,s64,b32,f32
                    if ins_opcode == "setp":
                        reg_digit = "1"
                        reg_type = "pred"
                    elif ins_opcode == "mul" or ins_opcode == "mad":
                        if ins_str_list[1] == "wide":
                            reg_digit = str(int(re.sub("[^0-9]", "", reg_str)) * 2)
                        else:
                            reg_digit = re.sub("[^0-9]", "", reg_str)
                        reg_type = re.sub("[^a-z]", "", reg_str)
                    else:
                        reg_digit = re.sub("[^0-9]", "", reg_str)
                        reg_type = re.sub("[^a-z]", "", reg_str)


                des_reg = des_str.split(',')[0]
                return ins_opcode, reg_digit, reg_type, des_reg, reg_str

"""
- Fault inject function: Inject one fault
- Input: Line number of target instruction, thread dimension, random thread id x, random thread id y,
         thread x register, thread y register, loop register, destination register type, fault value, destination register digit,
         destination register, label number, isntruction type, register str, last param, random loop depth for FI
- Output: generate modified PTX file for FI
"""

# fault injection
def inject_one_fault(target_line,
                     thread_num,
                     target_x, target_y,
                     com_thread_x, com_thread_y,
                     loop_reg,
                     reg_type,
                     fault_value,
                     reg_digit,
                     dest_reg,
                     label_num,
                     instruction_type,
                     reg_str,
                     last_param,
                     ran_loop
                     ):
    line_num = 0
    pred_reg_num = 0
    rd_reg_num = 0
    pfile = open(ptx_file, "w")
    bfile = open(back_file, 'r')


    for line in bfile.readlines():
        line_num += 1

        # not in a loop
        if in_loop(target_line) == '0':
            # thread 1
            if thread_num == 1:
                
                if line.strip().startswith('.reg'):
                    type_item = line.strip().split()[1]  
                    if type_item == ".pred":
                        pred_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  
                        after_pred = int(pred_reg_num) + 1  
                        str_1 = ".reg .pred   %p<" + str(after_pred) + ">;"
                        pfile.write('    ' + str_1 + '\n')  
                    # elif type_item == ".s64":
                    #     rd_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  
                    #     after_rd = int(rd_reg_num) + 1  
                    #     str_1 = ".reg .s64   %rd<" + str(after_rd) + ">;"
                    #     pfile.write('    ' + str_1 + '\n')  
                    else:
                        pfile.write(line)  

                # target line
                elif line_num == int(target_line):
                    pfile.write(line)
                    # target_x, target_y = random_thread2(thread_x, thread_y)  
                    
                    if reg_type == "pred":
                        insert_str1 = "setp.eq." + str(instruction_type) + " " + "%p" + str(pred_reg_num) \
                                      + "," + str(com_thread_x) + ", " + str(target_x) + ";"
                        insert_str2 = "@!%p" + str(pred_reg_num) + "  bra BB0_100;"
                        #insert_str3 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        #insert_str4 = "st.global.s32 [%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        insert_str5 = "xor.pred    " + str(dest_reg) + ", " + str(dest_reg) + ", 0x1;"
                        #insert_str6 = "st.global.s32 [%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str7 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        #pfile.write('       ' + insert_str3 + '\n')
                        #pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        #pfile.write('       ' + insert_str6 + '\n')
                        pfile.write(insert_str7 + '\n')
                        pass

                    else:

                        insert_str1 = "setp.eq." + str(instruction_type) + " " + "%p" + str(pred_reg_num) \
                                      + "," + str(com_thread_x) + ", " + (str(target_x)) + ";"
                        insert_str2 = "@!%p" + (str(pred_reg_num)) + "  bra BB0_100;"
                        # insert_str3 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # insert_str4 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        insert_str5 = "xor.b" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(dest_reg) + ", " \
                                      + str(fault_value) + ";"
                        # insert_str6 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str7 = "BB0_100:"



                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        # pfile.write('       ' + insert_str3 + '\n')
                        # pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        # pfile.write('       ' + insert_str6 + '\n')
                        pfile.write(insert_str7 + '\n')

                else:
                    pfile.write(line)
            # thread 2
            else:
                # change reg number
                if line.strip().startswith('.reg'):
                    type_item = line.strip().split()[1]  # get reg-type, eg .pred .f32
                    if type_item == ".pred":
                        pred_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  
                        after_pred = (int(pred_reg_num) + 3)  
                        str_1 = ".reg .pred   %p<" + str(after_pred) + ">;"
                        pfile.write('    ' + str_1 + '\n')  
                    # elif type_item == ".s64":
                    #     rd_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  
                    #     after_rd = (int(rd_reg_num) + 1)  
                    #     str_1 = ".reg .s64   %rd<" + str(after_rd) + ">;"
                    #     pfile.write('    ' + str_1 + '\n')  
                    else:
                        pfile.write(line)  

                # if target line
                elif line_num == int(target_line):
                    # write to ptx
                    pfile.write(line)
                    # target_x, target_y = random_thread2(thread_x, thread_y)
                    if reg_type == "pred":
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(temp_pred1) + 1

                        insert_str1 = "setp.eq." + str(instruction_type) + " " + "%p" + str(pred_reg_num) \
                                      + "," + str(com_thread_x) + "," + (str(target_x)) + ";"

                        insert_str2 = "setp.eq." + str(instruction_type) + " " + "%p" + (str(temp_pred1)) \
                                      + "," + str(com_thread_y) + "," + (str(target_y)) + ";"

                        insert_str3 = "and.pred    %p" + (str(temp_pred2)) + ", %p" + str(pred_reg_num) + ", %p" + (
                            str(temp_pred1)) + ";"
                        
                        insert_str4 = "@!%p" + (str(temp_pred2)) + "  bra BB0_100;"

                        # insert_str5 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # insert_str6 = "st.global.s32 [%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        insert_str7 = "xor.pred    " + str(dest_reg) + ", " + str(dest_reg) + ", 0x1;"
                        #insert_str8 = "st.global.s32 [%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str9 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        # pfile.write('       ' + insert_str5 + '\n')
                        # pfile.write('       ' + insert_str6 + '\n')
                        pfile.write('       ' + insert_str7 + '\n')
                        #pfile.write('       ' + insert_str8 + '\n')
                        pfile.write(insert_str9 + '\n')
                        pass

                    else:
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(temp_pred1) + 1

                        insert_str1 = "setp.eq." + str(instruction_type) + " " + "%p" + str(pred_reg_num) \
                                      + ", " + str(com_thread_x) + ", " + (str(target_x)) + ";"

                        insert_str2 = "setp.eq." + str(instruction_type) + " " + "%p" + (str(temp_pred1)) \
                                      + ", " + str(com_thread_y) + ", " + (str(target_y)) + ";"


                        insert_str3 = "and.pred    %p" + (str(temp_pred2)) + ", %p" + str(pred_reg_num) + ", %p" + (
                            str(temp_pred1)) + ";"

                        insert_str4 = "@!%p" + (str(temp_pred2)) + "  bra BB0_100" ";"
                        #insert_str5 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        #insert_str6 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        insert_str7 = "xor.b" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(dest_reg) + ", " \
                                      + str(fault_value) + ";"
                        #insert_str8 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str9 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        # pfile.write('       ' + insert_str5 + '\n')
                        # pfile.write('       ' + insert_str6 + '\n')
                        pfile.write('       ' + insert_str7 + '\n')
                        #pfile.write('       ' + insert_str8 + '\n')
                        pfile.write(insert_str9 + '\n')

                else:
                    pfile.write(line)



        else:

            if thread_num == 2:
                
                if line.strip().startswith('.reg'):
                    type_item = line.strip().split()[1]  
                    
                    if type_item == ".pred":
                        pred_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  
                        after_pred = (int(pred_reg_num) + 5)  
                        str_1 = ".reg .pred   %p<" + str(after_pred) + ">;"
                        pfile.write('    ' + str_1 + '\n')  # 将修改后的pred写入ptx
                    elif type_item == ".b32":
                        rd_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])  
                        after_rd = (int(rd_reg_num) + 1)  
                        str_1 = ".reg .b32   %r<" + str(after_rd) + ">;"
                        pfile.write('    ' + str_1 + '\n')  
                    else:
                        pfile.write(line)  
                
                elif line_num == int(target_line):
                    print("====================" + str(ran_loop) + " in 64 times==============")
                    pfile.write(line)  
                    # target_x, target_y = random_thread2(thread_x, thread_y)  
                    
                    if reg_type == "pred":
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(temp_pred1) + 1
                        temp_pred3 = int(temp_pred2) + 1
                        temp_pred4 = int(temp_pred3) + 1
                        
                        insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                      + ", " + str(loop_reg) + ", " + str((ran_loop - 1) * 8 - 512) + ";"
                        
                        insert_str2 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + "," + str(com_thread_x) + ", " + (str(target_x)) + ";"
                        
                        insert_str3 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + "," + str(com_thread_y) + ", " + (str(target_y)) + ";"

                        insert_str4 = "and.pred    %p" + (str(temp_pred3)) + ", %p" + (str(temp_pred1)) \
                                       + ", %p" + (str(temp_pred2)) + ";"
                        insert_str5 = "and.pred    %p" + (str(temp_pred4)) + ", %p" + (str(temp_pred3)) \
                                       + ", %p" + (str(pred_reg_num)) + ";"
                        insert_str6 = "@!%p" + (str(temp_pred4)) + " bra BB0_100;"
                        # insert_str7 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # insert_str8 = "st.global.s32 [%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        insert_str9 = "xor.pred " + (str(dest_reg)) + ", " + str(dest_reg) + ", 0x1;"
                        #insert_str10 = "st.global.s32 [%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str11 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        pfile.write('       ' + insert_str6 + '\n')
                        # pfile.write('       ' + insert_str7 + '\n')
                        # pfile.write('       ' + insert_str8 + '\n')
                        pfile.write('       ' + insert_str9 + '\n')
                        #pfile.write('       ' + insert_str10 + '\n')
                        pfile.write(insert_str11 + '\n')
                        pass
                    
                    else:
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(temp_pred1) + 1
                        temp_pred3 = int(temp_pred2) + 1
                        temp_pred4 = int(temp_pred3) + 1

                        insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                      + ", " + str(loop_reg) + ", " + str((ran_loop - 1) * 8 - 512) + ";"
                        
                        insert_str2 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + "," + str(com_thread_x) + ", " + (str(target_x)) + ";"
                        
                        insert_str3 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + "," + str(com_thread_y) + ", " + (str(target_y)) + ";"

                        insert_str4 = "and.pred    %p" + (str(temp_pred3)) + ", %p" + (str(temp_pred1)) \
                                      + ", %p" + (str(temp_pred2)) + ";"
                        insert_str5 = "and.pred    %p" + (str(temp_pred4)) + ", %p" + (str(temp_pred3)) \
                                      + ", %p" + (str(pred_reg_num)) + ";"
                        insert_str6 = "@!%p" + (str(temp_pred4)) + " bra BB0_100;"
                        #insert_str7 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # #insert_str8 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "]," \
                        #               + str(dest_reg) + ";"
                        # change
                        insert_str9 = "xor.b" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(dest_reg) + ", " \
                                      + str(fault_value) + ";"
                        # #insert_str10 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "+8]," + \
                        #               str(dest_reg) + ";"
                        insert_str11 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        pfile.write('       ' + insert_str5 + '\n')
                        pfile.write('       ' + insert_str6 + '\n')
                        #pfile.write('       ' + insert_str7 + '\n')
                        #pfile.write('       ' + insert_str8 + '\n')
                        pfile.write('       ' + insert_str9 + '\n')
                        #pfile.write('       ' + insert_str10 + '\n')
                        pfile.write(insert_str11 + '\n')
                else:
                    pfile.write(line)


            else:

                if line.strip().startswith('.reg'):
                    type_item = line.strip().split()[1]
                    if type_item == ".pred":
                        pred_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])
                        after_pred = (int(pred_reg_num) + 3)  
                        pfile.write(line.replace(str(pred_reg_num), str(after_pred)))

                    elif type_item == ".b32":
                        rd_reg_num = re.sub("[^0-9]", "", line.strip().split()[2])
                        after_rd = (int(rd_reg_num) + 1)
                        str_1 = ".reg .b32   %rd<" + str(after_rd) + ">;"
                        pfile.write('    ' + str_1 + '\n')

                    else:
                        pfile.write(line)

                elif line_num == int(target_line):
                    print("====================" + str(ran_loop) + " in 64 times==============")
                    pfile.write(line)  
                    # target_x, target_y = random_thread2(thread_x, thread_y)  
                    
                    if reg_type == "pred":
                       
                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(pred_reg_num) + 2
                        
                        insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                      + ", " + str(loop_reg) + ", " + str((ran_loop - 1) * 8 - 512) + ";"
                        
                        insert_str2 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + "," + str(com_thread_x) + ", " + (str(target_x)) + ";"
                        insert_str3 = "and.pred    %p" + (str(temp_pred2)) + ", %p" + (str(temp_pred1)) + ", %p" + (str(pred_reg_num)) + ";"
                        insert_str4 = "@!%p" + (str(temp_pred2)) + " bra BB0_100;"
                        # insert_str5 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # insert_str6 = "st.global.s32 [%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        insert_str7 = "xor.pred" + (str(dest_reg)) + ", " + (str(dest_reg)) + ", 0x1;"
                        #insert_str8 = "st.global.s32 [%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str9 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        # pfile.write('       ' + insert_str5 + '\n')
                        # pfile.write('       ' + insert_str6 + '\n')
                        pfile.write('       ' + insert_str7 + '\n')
                        #pfile.write('       ' + insert_str8 + '\n')
                        pfile.write(insert_str9 + '\n')


                    else:

                        temp_pred1 = int(pred_reg_num) + 1
                        temp_pred2 = int(pred_reg_num) + 2


                        insert_str1 = "setp.eq." + str(instruction_type) + " %p" + str(pred_reg_num) \
                                       + ", " + str(loop_reg) + ", " + str((ran_loop - 1) * 8 - 512) + ";"

                        insert_str2 = "setp.eq." + str(instruction_type) + " %p" + str(temp_pred1) \
                                      + ", " + str(com_thread_x) + ", " + (str(target_x)) + ";"
                        insert_str3 = "and.pred    %p" + (str(temp_pred2)) + ", %p" + (str(temp_pred1)) + ", %p" + (str(pred_reg_num)) + ";"
                        insert_str4 = "@!%p" + (str(temp_pred2)) + " bra BB0_100;"
                        # insert_str5 = "ld.param.u64 %rd" + str(rd_reg_num) + ", " + str(last_param) + ";"
                        # insert_str6 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "]," + str(dest_reg) + ";"
                        # change
                        insert_str7 = "xor.b" + str(reg_digit) + "    " + str(dest_reg) + ", " + str(dest_reg) + ", " \
                                      + str(fault_value) + ";"
                        #insert_str8 = "st.global." + str(reg_str) + " " + "[%rd" + str(rd_reg_num) + "+8]," + str(dest_reg) + ";"
                        insert_str9 = "BB0_100:"

                        pfile.write('       ' + insert_str1 + '\n')
                        pfile.write('       ' + insert_str2 + '\n')
                        pfile.write('       ' + insert_str3 + '\n')
                        pfile.write('       ' + insert_str4 + '\n')
                        # pfile.write('       ' + insert_str5 + '\n')
                        # pfile.write('       ' + insert_str6 + '\n')
                        pfile.write('       ' + insert_str7 + '\n')
                        #pfile.write('       ' + insert_str8 + '\n')
                        pfile.write(insert_str9 + '\n')
                else:
                    pfile.write(line) 

    pfile.close()
    bfile.close()

"""
- Main function
"""

def main():
    itera_time = int(sys.argv[1])
    thread_num = 2
    thread_x = 512     # modify
    thread_y = 512     # modify
    instruction_type = "b32"
    ran_loop = 0
    # 1 make keep and 2 make dry
    # 3 delete extra lines in dryrun.out
    # 4 backup -> back_ptx
    # 5 generate temp.ptx
    # 6 get label number
    label_num = get_label()
    # 7 ins list
    ins_list = instruction_list()
    # 8 target line number
    target_line = inject_line_num(ins_list)
    # 9 kernel number and kernel name
    kernel_num, kernel_dict = get_kernel_info()
    kernel_name, last_param = get_kernel_name_param(target_line, kernel_dict)
    print(str(kernel_name) + "-----" + str(last_param))
    # 10 analyze target ins
    ins_opcode, reg_digit, reg_type, des_reg, reg_str = analyze_ins(target_line)
    # 11 fault value
    fault_value, bit = random_bit(reg_digit)
    # 12 is in loop, loop depth
    loop = in_loop(target_line)
    if loop == '1':
        ran_loop = random_loop_time(thread_x)
    # 13 compare thread id
    com_thread_x = '%r20'
    com_thread_y = '%r8'
    # 14 loop reg
    loop_reg = "%r21"


    # 12 Fault injection
    target_x, target_y = random_thread2(thread_x, thread_y)
    # print(sys.argv[2])
    # print(sys.argv[3])
    # target_x = int(sys.argv[2])
    # target_y = int(sys.argv[3])
    inject_one_fault(target_line, thread_num, target_x, target_y, com_thread_x, com_thread_y, loop_reg, reg_type, fault_value, reg_digit, des_reg,
                     label_num, instruction_type,reg_str,last_param,ran_loop)
    f = open(basic_file, 'a')
    f.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}\n".format(itera_time, app_name, kernel_name, target_x,
                                                                         target_y, bit, fault_value, target_line,
                                                                         ins_opcode, reg_digit, reg_type, des_reg,ran_loop))
    f.close()


if __name__ == "__main__":
    main()
