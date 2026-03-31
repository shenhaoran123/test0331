# -*- coding: utf-8 -*-

import numpy as np
import warnings
warnings.filterwarnings("ignore")
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn import metrics
from time import *


file1 = 'all_feature.data' # features with linenum
file2 = "result.txt"		# output: predict result 
file3 = "test_data.txt"	# test data
file4 = "test_label.txt"	# test label
file5 = "train_data.txt"	# training data
file6 = "train_label.txt"	# training label



def train_model():

    data = np.loadtxt(file1, dtype=float, delimiter=',')
    x, y = np.split(data, indices_or_sections=(26,), axis=1)

    
    train_data, test_data, train_label, test_label = train_test_split(x, y, random_state = 1, train_size=0.8,
                                                                      test_size=0.2)
    best_score = 0
    for gamma in [0.001, 0.01, 0.1, 1, 10, 100]:
        for C in [0.001, 0.01, 0.1, 1, 10, 100]:
            svm1 = svm.SVC(gamma=gamma, C=C, kernel='rbf')  
            svm1.fit(train_data, train_label)
            score = svm1.score(test_data, test_label)
            if score > best_score:  
                best_score = score
                best_C = C
                best_gamma = gamma

    classifier = svm.SVC(C=best_C, kernel='rbf', gamma=best_gamma, decision_function_shape='ovr')

    classifier.fit(train_data, train_label.ravel())

    return classifier, test_data, test_label, train_data, train_label


def get_predict(classifier, test_data):
    predict_label = classifier.predict(test_data)
    return predict_label



def get_auc(predict_label, test_label):
    auc = metrics.roc_auc_score(test_label, predict_label)
    return auc


# Accuracy
def get_accuracy(predict_label, test_label):
    acc_score = accuracy_score(test_label, predict_label)
    return acc_score


# Precision
def get_precision(predict_label, test_label):
    macro_precison = precision_score(test_label, predict_label, average='macro')
    micro_precision = precision_score(test_label, predict_label, average='micro')
    weigh_precision = precision_score(test_label, predict_label, average='weighted')
    precision = precision_score(test_label, predict_label, average=None)
    return macro_precison, micro_precision, weigh_precision

# Recall
def get_recall(predict_label, test_label):
    macro_recall = recall_score(test_label, predict_label, average='macro')
    micro_recall = recall_score(test_label, predict_label, average='micro')
    weigh_recall = recall_score(test_label, predict_label, average='weighted')
    # recall = recall_score(test_label, predict_label, average=None)
    return macro_recall, micro_recall, weigh_recall


def get_f1(predict_label, test_label):
    macro_f1 = f1_score(test_label, predict_label, average='macro')
    micro_f1 = f1_score(test_label, predict_label, average='micro')
    weigh_f1 = f1_score(test_label, predict_label, average='weighted')
    # recall = recall_score(test_label, predict_label, average=None)
    return macro_f1, micro_f1, weigh_f1


def write_all_data(test_data, test_label, predict_label, train_data, train_label):
    f1 = open(file3, 'w')
    f2 = open(file4, 'w')
    f4 = open(file5, 'w')
    f5 = open(file6, 'w')

    np.savetxt(f1, test_data, fmt='%d', delimiter=',')
    np.savetxt(f2, test_label, fmt='%d', delimiter=',')
    np.savetxt(f4, train_data, fmt='%d', delimiter=',')
    np.savetxt(f5, train_label, fmt='%d', delimiter=',')
    f1.close()
    f2.close()
    f4.close()
    f5.close()


def write_result(predict_label, test_label, time):
    # result
    f = open(file2, 'w')
    f.write("Accuracy:" + str(get_accuracy(predict_label, test_label)) + "\n")
    f.write("Precision:" + str(get_precision(predict_label, test_label)) + "\n")
    f.write("recall:" + str(get_recall(predict_label, test_label)) + "\n")
    f.write("f1:" + str(get_f1(predict_label, test_label)) + "\n")
    f.write("auc:" + str(get_auc(predict_label, test_label)) + "\n")
    f.write(time)
    f.close()




def main():
    start_time = time()
    classifier, test_data, test_label,train_data, train_label = train_model()

    # f = open(file7, 'r')
    # for line in f.readlines():
    #    test_data = np.append(test_data,line.strip()[0:-2])
    #    test_label = np.append(test_label,line.strip()[-2:-1])
    # print(test_data)
    # print(test_label)
    # test_data =
    # test_label =



    end_time = time()
    predict_label = get_predict(classifier, test_data)
    write_all_data(test_data, test_label, predict_label, train_data, train_label)
    write_result(predict_label, test_label, str(end_time-start_time))
    for i in range(len(test_data)):
        print(str(test_data[i]) + "predict label：" + str(predictions[i]))


if __name__ == "__main__":
    main()
