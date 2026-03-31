# -*- coding: utf-8 -*-

import re

file1 = "2mm1.ptx"
file4 = "dep_list.txt"
file7 = "real.txt"

file2 = "ins.txt"          
file3 = "ins_feature.txt"   
file5 = "all_feature.data"  
file8 = "line_feature.data"    
file6 = "ins2.txt"          



# line_num ins_type  dest_reg_type1  dest_reg_bit  operand_num  dest_reg_type2
def get_ins():
    line_num = 0  
    f1 = open(file1, 'r')
    f2 = open(file2, 'w')

    for line in f1.readlines():
        line_num += 1
        analyze_line = line.strip()
        if analyze_line.startswith('// .globl'):
            continue
        if analyze_line == "":
            continue
        if analyze_line.startswith('//'):
            continue
        if analyze_line.startswith('.'):
            continue
        if analyze_line.startswith('BB'):
            continue
        if analyze_line.startswith('(') or analyze_line.startswith(')'):
            continue
        if analyze_line.startswith('}') or analyze_line.startswith('{'):
            continue
        # if analyze_line.startswith('@'):
        #     continue
        if analyze_line.startswith('ret'):
            continue
        if analyze_line.startswith('bra'):
            continue
        else:
            f2.write(str(line_num))  
            ins_num = len(analyze_line.split())
            ins_str = analyze_line.split()[0]
            reg_str = analyze_line.split()[1]
            reg_operand = re.sub('[0-9]', '', reg_str.replace(',', '').replace('%', ''))
            ins_operand_str = ins_str.split('.')[0]

            if ins_str.startswith('@'):
                ins_operand = '@'
                ins_type = re.sub("[^A_Za-z0-9]", "", ins_operand_str)
                ins_bit = "1"
            elif ins_str.startswith('and'):
                ins_operand = ins_str.split('.')[0]
                ins_type = ins_str.split('.')[-1]
                ins_bit = '1'
            else:
                ins_operand = ins_operand_str
                ins_type_str = ins_str.split('.')[-1]
                ins_type = re.sub("[0-9]", "", ins_type_str)
                ins_bit = re.sub("[^0-9]", "", ins_type_str)
            f2.write("\t" + ins_operand + "\t" + ins_type + "\t" + ins_bit + "\t" + str(ins_num - 2) + "\t" +
                     reg_operand + "\n")

    f1.close()
    f2.close()


def get_ins2():
    line_num = 0  
    f1 = open(file1, 'r')
    f2 = open(file6, 'w')

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
        # if analyze_line.startswith('@'):
        #     continue
        if analyze_line.startswith('ret'):
            continue
        else:
            f2.write(str(line_num))  
            f2.write(" " + analyze_line + "\n") 
    f1.close()
    f2.close()



def get_ins_feature():
    f1 = open(file2, 'r')   # ins.txt
    f2 = open(file3, 'w')   # ins_feature.txt

    for line in f1.readlines():
        analy_line = line.split()
        s = ''
        s += analy_line[0] + ' '
        s += analy_line[-2] + ','
        if (analy_line[1] == 'add' or analy_line[1] == 'sub') and (analy_line[2] == 'u' or analy_line[2] == 's'):
            s += '1,'
        else:
            s += '0,'
        if (analy_line[1] == 'add' or analy_line[1] == 'sub') and (analy_line[2] == 'f'):
            s += '1,'
        else:
            s += '0,'
        if (analy_line[1] == 'mul' or analy_line[1] == 'div') and (analy_line[2] == 'u' or analy_line[2] == 's'):
            s += '1,'
        else:
            s += '0,'
        if (analy_line[1] == 'mul' or analy_line[1] == 'div' or analy_line[1] == 'fma') and (analy_line[2] == 'f'):
            s += '1,'
        else:
            s += '0,'
        if analy_line[1] == 'setp':
            s += '1,'
        else:
            s += '0,'
        if (analy_line[1] == 'and' or analy_line[1] == 'or' or analy_line[1] == 'xor' or analy_line[1] == 'or') and \
                analy_line[2] == 'pred':
            s += '1,'
        else:
            s += '0,'
        if (analy_line[1] == 'and' or analy_line[1] == 'or' or analy_line[1] == 'xor' or analy_line[1] == 'or') and \
                analy_line[2] != 'pred':
            s += '1,'
        else:
            s += '0,'
        if analy_line[1] == 'shl':
            s += '1,'
        else:
            s += '0,'
        if analy_line[1] == 'shr':
            s += '1,'
        else:
            s += '0,'
        if analy_line[1] == 'ld':
            s += '1,'
        else:
            s += '0,'
        if len(analy_line) == 6:
            s += analy_line[3] + ','
        else:
            s += '0,'
        s += in_loop(str(analy_line[0]))
        s += '\n'
        f2.write(s)

    f1.close()
    f2.close()


def ins_feature(target_ins):
    # ins_feature.txt
    f = open(file3, 'r')
    for line in f.readlines():
        analy_line = line.split()
        if analy_line[0] == target_ins:
            return analy_line[1]
    return 'N'

def get_masked_ins():
    # ins.txt
    f1 = open(file2, 'r')
    ins_list = []
    
    for line in f1.readlines():
        a_line = line.split()
        if (a_line[1] == 'and' or a_line[1] == 'or') and (a_line[2] != 'pred'):
            ins_list.append(a_line[0])
        elif a_line[1] == 'shl':
            ins_list.append(a_line[0])
    f1.close()
    return ins_list


def address_ins():
	# ins.txt
    f1 = open(file2, 'r')
    address_list = []
    # bit_list = []
    for line in f1.readlines():
        analy_line = line.split()
        if analy_line[-1] == 'rd':
            address_list.append(analy_line[0])
        else:
            pass
    f1.close()
    return address_list


def get_loop_list():
    loop_list = ['59', '64', '147', '149']
    return loop_list



def get_bra_list():
    bra_list = ['38', '39', '40']
    return bra_list


def cmp_list():
    # ins.txt
    f1 = open(file2, 'r')
    cmp_list = []
    for line in f1.readlines():
        analy_line = line.split()
        if analy_line[1] == '@':
            cmp_list.append(str(int(analy_line[0]) - 1))
        else:
            pass
    f1.close()
    return cmp_list


def get_store():
    f = open(file2, 'r')
    store_list = []
    store_bit = []
    for line in f.readlines():
        analy_line = line.split()
        if analy_line[1] == 'st':
            store_list.append(analy_line[0])
            store_bit.append(analy_line[3])
        else:
            pass
    f.close()
    return store_list



def get_add_list():
    f1 = open(file2, 'r')
    add_list = []
    for line in f1.readlines():
        analy_line = line.split()
        # if analy_line[1] == 'add' and analy_line[-1] != 'rd':
        if analy_line[1] == 'add':
            add_list.append(analy_line[0])
    f1.close()
    return add_list


def get_mul_list():
    # ins.txt
    f1 = open(file2, 'r')
    cmul_list = get_constant_mul()
    mul_list = []
    for line in f1.readlines():
        analy_line = line.split()
        if analy_line[1] == 'mul' and analy_line[-1] != 'rd':
            if analy_line[0] not in cmul_list:
                mul_list.append(analy_line[0])
            else:
                pass

    f1.close()
    return mul_list

def in_loop(target_ins):

    target_ins = int(target_ins)
    if 59 <= target_ins <= 100 or 150 <= target_ins <= 191:
         return '1'
    else:
         return '0'

def get_constant_mul():
    f1 = open("ins2.txt", 'r')
    mul_list = []
    for line in f1.readlines():
        analy_line = line.split()
        if analy_line[1].split('.')[0] == 'mul':
            if re.sub("[^a-z]","",analy_line[2]) != 'rd':
                op = analy_line[-1].split(';')[0]
                if not op.startswith('%'):
                    mul_list.append(analy_line[0])
                else:
                    pass
    f1.close()
    return mul_list


def get_all_store():
    f1 = open(file4, 'r')
    f2 = open("store_list", 'w')
    st_list, st_bit = get_store()
    for line in f1.readlines():
        analy_line = line.strip().split(',')
        influ_st_list = []
        for i in range(1, len(analy_line) - 1):
            if analy_line[i] in st_list:
                influ_st_list.append(analy_line[i])
            else:
                pass
        f2.write(analy_line[0] + ' ' + str(len(influ_st_list)) + '\n')
    f1.close()
    f2.close()


def influ_ins(target_ins):
    # dep_list.txt
    f1 = open(file4, 'r')
    mask_list = get_masked_ins()
    is_mask = False
    influ_mask_ins = []
    address_list = address_ins()
    is_address = False
    influ_address_list = []

    loop_list = get_loop_list()
    is_loop_ins = False
    influ_loop_list = []

    bra_list = get_bra_list()
    is_bra = False
    influ_bra_list = []

    st_list = get_store()
    influ_st_list = []

    add_list = get_add_list()
    influ_add_list = []

    mul_list = get_mul_list()
    influ_mul_list = []

    cmul_list = get_constant_mul()
    influ_cmul_list = []

    influ_ins_num = 0

    for line in f1.readlines():
        analy_line = line.strip().split(',')
        # line number
        if analy_line[0] == target_ins:
            if target_ins in mask_list:
                is_mask = True
            else:
                is_mask = False

            if target_ins in address_list:
                is_address = True
            else:
                is_address = False

            if target_ins in loop_list:
                is_loop_ins = True
            else:
                is_loop_ins = False

            if target_ins in bra_list:
                is_bra = True
            else:
                is_bra = False

            influ_ins_num = len(analy_line) - 1
            for i in range(1, len(analy_line)):
                if analy_line[i] in address_list:
                    influ_address_list.append(analy_line[i])
                elif analy_line[i] in loop_list:
                    influ_loop_list.append(analy_line[i])
                elif analy_line[i] in bra_list:
                    influ_bra_list.append(analy_line[i])
                elif analy_line[i] in st_list:
                    influ_st_list.append(analy_line[i])
                elif analy_line[i] in mask_list:
                    influ_mask_ins.append(analy_line[i])
                elif analy_line[i] in add_list:
                    influ_add_list.append(analy_line[i])
                elif analy_line[i] in mul_list:
                    influ_mul_list.append(analy_line[i])
                elif analy_line[i] in cmul_list:
                    influ_cmul_list.append(analy_line[i])
        else:
            pass
    f1.close()
    s = ""
    if is_mask:
        s += '1,'
    else:
        s += '0,'
    if is_address:
        s += '1,'
    else:
        s += '0,'
    if is_loop_ins:
        s += '1,'
    else:
        s += '0,'
    if is_bra:
        s += '1,'
    else:
        s += '0,'
    s += str(len(influ_mask_ins)) + ','
    s += str(len(influ_address_list)) + ','
    if len(influ_loop_list) != 0:
        s += '1,'
    else:
        s += '0,'
    if len(influ_bra_list) != 0:
        s += '1,'
    else:
        s += '0,'
    s += str(len(influ_st_list)) + ','
    s += str(len(influ_add_list)) + ','
    s += str(influ_ins_num) + ','
    s += str(len(influ_cmul_list)) + ','
    s += str(len(influ_mul_list))

    return s

def get_line_feature():
    # real.txt
    f1 = open(file7, 'r')
    # line_feature**.data
    f2 = open(file8, 'w')
    

    for line in f1.readlines():
        analy_line = line.strip().split()
        line_num = analy_line[0]
        sdc_rate = analy_line[1]

        flow_feature = influ_ins(line_num)
        ins_fea = ins_feature(line_num)
        feature_list = flow_feature + "," + ins_fea
        if float(sdc_rate) >= 0.6:
            sdc_label = '1'
        else:
            sdc_label = '0'
        f2.write(line_num + ',' + feature_list + ',' + sdc_label + '\n')
        # f2.write(feature_list + '\n')
        # f3.write(sdc_label + '\n')
    f1.close()
    f2.close()
    

def get_all_feature():
    # con_result.txt
    f1 = open(file7, 'r',encoding = "gb18030",errors = "ignore")
    # all_feature**.data
    f2 = open(file5, 'w')

    for line in f1.readlines():
        analy_line = line.strip().split()
        line_num = analy_line[0]
        sdc_rate = analy_line[1]
        ins_fea = ins_feature(line_num)
        feature_list = ins_fea
        if float(sdc_rate) >= 0.6:
            sdc_label = '1'
        else:
            sdc_label = '0'
        f2.write(feature_list + ',' + sdc_label + '\n')

    f1.close()
    f2.close()




def main():
    get_ins()
    get_ins2()
    get_ins_feature()
    get_all_feature()


if __name__ == "__main__":
    main()
