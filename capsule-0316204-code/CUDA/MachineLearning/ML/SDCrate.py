def sdc_rate():
    f1 = open("result_test.txt",'r')
    f2 = open("sdc_rate.txt",'w')

    dict1 = {}


    for line in f1.readlines():
        ana_line = line.strip().split(',')
        ins_num = ana_line[7]
        if ins_num not in dict1:
            dict1.setdefault(ins_num,'0+0')
        va = str(dict1.get(ins_num)).split('+')
        if ana_line[15] == 'SDC':
            va[0] = int(va[0])+1
            va[1] = int(va[1])+1
            value = str(va[0])+'+'+str(va[1])
            dict1[ins_num] = value
        else:
            va[0] = int(va[0]) + 1
            value = str(va[0]) + '+' + str(va[1])
            dict1[ins_num] = value
        # elif ana_line[12] == 'SDC_UNACCEPTABLE':
        #     va[0] = int(va[0]) + 1
        #     va[1] = int(va[1]) + 1
        #     value = str(va[0]) + '+' + str(va[1])
        #     dict1[ins_num] = value
        # elif ana_line[12] == 'DUE':
        #     va[0] = int(va[0]) + 1
        #     va[1] = int(va[1]) + 1
        #     value = str(va[0]) + '+' + str(va[1])
        #     dict1[ins_num] = value
        # elif ana_line[12] == 'Masked':
        #     va[0] = int(va[0]) + 1
        #     value = str(va[0]) + '+' + str(va[1])
        #     dict1[ins_num] = value


    for key in dict1.keys():
        print(str(key)+','+dict1.get(key))
        value = dict1.get(key).strip().split('+')
        rate = int(value[1])/int(value[0])
        f2.write(str(key)+','+str(rate)+'\n')

def main():

    sdc_rate()



if __name__ == "__main__":
    main()


