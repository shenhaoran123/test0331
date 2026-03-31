# -*- coding: utf-8 -*-

import os
import numpy as np
import sys


"""
-- Parse Difference (PD): Classify the output of individual fault injection: Masked, SDC, Detected
   PD - V1.0 - July 31, 2023
   Nan Jiang
   College of Computer Science and Technology, Jilin University
"""


stderr_file = "stderr.txt"
stdout_file = "stdout.txt"
output_file = "out.txt"
back_output = "back_output.txt"
diff_file = "diff.log"
golden_output = "golden/out.txt"
back_golden = "backup_golden_output.txt"
outcome_file = "outcome.txt"

outcome = 0

metric = 0

# Classify the output of individual fault injection: Masked, SDC, Detected

"""
- Classify the output of individual fault injection: Masked, SDC, Detected
- Metric: rel-l2 norm/rel-error
"""

# read program return value from shell script
para = int(sys.argv[1])
print("para:",para)
itera_time = int(sys.argv[2])
print("itera_time:",itera_time)
if os.path.exists(stderr_file):
    line_num = 0
    stdout = open(stdout_file, 'r')
    std_time = 0.0018
    for line in stdout.readlines():
        line_num += 1
        if line_num == 2:
            time = float(line.split()[-1][0:-1])
    size = os.path.getsize(stderr_file)
    print(size,"stderr_file")
    if size != 0:
        outcome = 1
        metric = sys.maxsize
        print("======================Error file not null===========================")
    elif para != 0:
        outcome = 1
        metric = sys.maxsize
        print("=========================Do not return 0 correctly==============================")
    # elif time > 0.0018 * 10:
    #     outcome = 1
    #     metric = sys.maxsize
    else:
        if os.path.getsize(diff_file) == 0:
            # Masked
            print('======================Masked==============================')
            outcome = 2
        else:
            print('~~~~~~~~~~~~~~~~~~~~~~~~SDC~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            outcome = 3
            # SDC difference
            f1 = open(output_file, 'r')  # output of FI 
            f2 = open(back_output, 'w')  # backup of output of FI 
            for line in f1.readlines():
                f2.write(line[0:-2].replace("\t", ","))
                f2.write("\n")
            f1.close()
            f2.close()

            f1 = open(golden_output, "r")  # golden output
            f2 = open(back_golden, "w")  # backup for golden output
            for line in f1.readlines():
                f2.write(line[0:-2].replace("\t", ","))
                f2.write("\n")
            f1.close()
            f2.close()

            golden_output = np.loadtxt(back_golden, delimiter=",")
            corrupted_output = np.loadtxt(back_output, delimiter=",")
            diff_matrix = corrupted_output - golden_output
            # rel-l2
            diff_sum = 0
            golden_sum = 0
            m, n = np.shape(diff_matrix)
            for i in range(m):
                for j in range(n):
                    diff_sum += np.square(diff_matrix[i, j])
                    golden_sum += np.square(golden_output[i, j])

            metric = np.sqrt(diff_sum / golden_sum)

            if metric==1.0:
                outcome=1

f = open(outcome_file, 'a')
if outcome == 1:
    f.write("{0},{1},{2}\n".format(itera_time, "DUE", metric))
elif outcome == 2:
    f.write("{0},{1},{2}\n".format(itera_time, "Masked", metric))
else:
    f.write("{0},{1},{2}\n".format(itera_time, "SDC", metric))
f.close()
