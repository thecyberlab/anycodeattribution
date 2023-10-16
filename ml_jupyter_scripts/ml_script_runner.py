from collections import OrderedDict
from datetime import timedelta
import statistics
import time
import gc
import sys
import numpy as np
import pandas as pd
import seaborn as sns

import json
import operator
import os

from sklearn import metrics
from sklearn import preprocessing

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier

import matplotlib.pyplot as plt

from tabulate import tabulate

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

current_dir = os.getcwd() + '/ML_Results/'

cmd_directory = str(sys.argv[-2])
main_directory = os.path.dirname(cmd_directory)
feature = str(sys.argv[-1])

class_accuracy_output = current_dir + feature + '_class_accuracy_output.txt'

print('Entered ML Python script')
print(main_directory)
print(feature)

categoric_kothari = ['author', 'file']
colsToDrop_kothari = ['file']

categoric_ding = ['Author', 'File']
colsToDrop_ding = ['File']

categoric_caliskan = ['Author', 'FilePath', 'Basename', 'Lines-Group']
colsToDrop_caliskan = ['FilePath', 'Basename', 'Lines-Group']

categoric_zaffar = ['Author', 'FilePath', 'Basename', 'Extension', 'Encoding']
colsToDrop_zaffar = ['FilePath', 'Basename', 'Extension', 'Encoding']

categoric_abazari = ['Author', 'FilePath', 'Basename', 'Extension', 'Encoding']
colsToDrop_abazari = ['FilePath', 'Basename', 'Extension', 'Encoding']

if 'kothari' in feature:
    folder_name = "kothari_results"
    csv_file = main_directory + '/' + folder_name + '/' + folder_name + '_kothari_results.csv'
    categoric = categoric_kothari
    colsToDrop = colsToDrop_kothari
    label = 'author'
elif 'ding' in feature:
    folder_name = "ding_results"
    csv_file = main_directory + '/' + folder_name + '/' + folder_name + '_ding_results.csv'
    categoric = categoric_ding
    colsToDrop = colsToDrop_ding
    label = 'Author'
elif 'caliskan' in feature:
    folder_name = "caliskan_results"
    csv_file = main_directory + '/' + folder_name + '/' + folder_name + '_caliskan_results.csv'
    categoric = categoric_caliskan
    colsToDrop = colsToDrop_caliskan
    label = 'Author'
elif 'zaffar' in feature:
    folder_name = "zaffar_results"
    csv_file = main_directory + '/' + folder_name + '_IG_stats.csv'
    categoric = categoric_zaffar
    colsToDrop = colsToDrop_zaffar
    label = 'Author'
elif 'abazari' in feature:
    folder_name = "abazari_results"
    csv_file = main_directory + '/' + folder_name + '_IG_stats.csv'
    categoric = categoric_abazari
    colsToDrop = colsToDrop_abazari
    label = 'Author'
else:
    AssertionError("File Not found")
start_time = time.time()

original = pd.read_csv(
    csv_file,
    engine='c',
    low_memory=False
)

gc.collect()

original.fillna(0)

print("Categoric columns:", categoric)
for col in original.columns:
    if col in categoric:
        original[col] = pd.Categorical(original[col])

print("Cols to drop", colsToDrop)

original.drop(columns=colsToDrop, inplace=True)

gc.collect()

# REMOVE COLUMNS WITH VARIANCE ZERO
original = original.drop(original.columns[original.nunique() == 1], axis=1)

gc.collect()

print("Label: ", label)
labels = np.array(original[label])
original.drop(label, axis=1, inplace=True)

gc.collect()

# STANDARDIZE DATA
standard_scaler = preprocessing.StandardScaler()  # fit and transform the data

features = pd.DataFrame(standard_scaler.fit_transform(original.values),
                        columns=original.columns,
                        index=original.index)


# split value must be equal or less to the least frequncy of a particular target
xspl = StratifiedKFold(n_splits=4,
                       shuffle=True,
                       random_state=42)

# we use only _ONE_ slice of the set
for train_index, test_index in xspl.split(features, labels):
    X_train, X_test = features.iloc[train_index], features.iloc[test_index]
    y_train, y_test = labels[train_index], labels[test_index]
    break

def compute_models(data_x, data_y, train_X, train_y, test_X, test_y):
    # Create classifiers
    gnb = GaussianNB()

    # other options = hidden_layer_sizes=(10, 10, 10), random_state=42
    net = MLPClassifier(max_iter=10000,
                        learning_rate='adaptive',
                        solver='adam',
                        alpha=1)

    dec = DecisionTreeClassifier(max_depth=100)

    lda = LinearDiscriminantAnalysis()

    # USING WEKA defaults
    # criterion -> entropy
    # number of folds -> 3
    # minimum variance for split -> 1e-3
    # size of each bag -> 100
    # number of trees -> 100
    # number attributes -> 0 for unlimited
    # number of instances per leaf -> 2
    raf = RandomForestClassifier(n_estimators=100,
                                 n_jobs=1,
                                 max_depth=None,
                                 min_samples_split=2,
                                 min_samples_leaf=1,
                                 bootstrap=True,
                                 oob_score=True,  # Out of bag estimation only available if bootstrap=True"
                                 # bootstrap = False,
                                 max_features='log2',
                                 max_leaf_nodes=None,
                                 min_impurity_decrease=0.0,
                                 warm_start=False,
                                 # criterion = 'gini', # Gini impurity
                                 criterion='entropy',  # Information gain
                                 random_state=42,
                                 )

    etc = ExtraTreesClassifier(n_estimators=100,
                               n_jobs=1,
                               max_depth=None,
                               min_samples_split=2,
                               min_samples_leaf=1,
                               bootstrap=True,
                               oob_score=True,  # Out of bag estimation only available if bootstrap=True"
                               # bootstrap = False,
                               max_features='log2',
                               max_leaf_nodes=None,
                               min_impurity_decrease=0.0,
                               warm_start=False,
                               # criterion = 'gini', # Gini impurity
                               criterion='entropy',  # Information gain
                               random_state=42,
                               )

    models = [
        [dec, "DecisionTree"],  # Finishes
        [etc, "ExtraTreesClassifier"],
        [raf, "RandomForest"],  # Finishes
        [net, "Neural-Net"],  # Finishes
        [gnb, "GaussianNB"],  # Finishes
        [lda, "LinearDiscriminant"],  # Finishes
    ]

    inter_cv_res = OrderedDict()
    results = list()

    for item in models:
        model_start_time = time.time()

        model = item[0]
        desc = item[1]

        print("RUNNING --> ", desc)

        # Implementation
        model.fit(train_X, train_y)

        # Scoring
        xcross = cross_validation(model, data_x, data_y)

        accuracy_cv = xcross[0]
        accuracy_cv_std = xcross[1]
        accuracy_cv_folds = xcross[2]
        accuracy_cv_scores = xcross[3]
        accuracy_cv_min = xcross[4]
        accuracy_cv_max = xcross[5]

        model_end_time = time.time()
        model_elapsed = int(str(model_end_time - model_start_time).split(".")[0])
        model_elapsed_str = str(timedelta(seconds=model_elapsed))

        res = [desc,
               accuracy_cv,
               accuracy_cv_std,
               accuracy_cv_folds,
               accuracy_cv_min,
               accuracy_cv_max,
               model_elapsed_str,
               ]

        results.append(res)
        inter_cv_res[desc] = accuracy_cv_scores

        print(model, desc, results, inter_cv_res)

    return results, inter_cv_res

def prepare_results(list_results):
    list_acc = list()
    list_micro_precision = list()
    list_micro_recall = list()
    list_micro_f1 = list()
    list_macro_precision = list()
    list_macro_recall = list()
    list_macro_f1 = list()
    list_weighted_precision = list()
    list_weighted_recall = list()
    list_weighted_f1 = list()
    list_macro_roc_auc_ovo = list()
    list_weighted_roc_auc_ovo = list()
    list_macro_roc_auc_ovr = list()
    list_weighted_roc_auc_ovr = list()

    for k, vs in list_results.items():
        list_acc.append(vs[0])
        list_micro_precision.append(vs[2])
        list_micro_recall.append(vs[3])
        list_micro_f1.append(vs[4])
        list_macro_precision.append(vs[5])
        list_macro_recall.append(vs[6])
        list_macro_f1.append(vs[7])
        list_weighted_precision.append(vs[8])
        list_weighted_recall.append(vs[9])
        list_weighted_f1.append(vs[10])

        list_macro_roc_auc_ovo.append(vs[11])
        list_weighted_roc_auc_ovo.append(vs[12])
        list_macro_roc_auc_ovr.append(vs[13])
        list_weighted_roc_auc_ovr.append(vs[14])

    cv_accuracy = statistics.mean(list_acc)
    cv_accuracy_std = statistics.stdev(list_acc)
    cv_accuracy_min = min(list_acc)
    cv_accuracy_max = max(list_acc)

    cv_micro_precision = statistics.mean(list_micro_precision)
    cv_micro_precision_std = statistics.stdev(list_micro_precision)
    cv_micro_precision_min = min(list_micro_precision)
    cv_micro_precision_max = max(list_micro_precision)

    cv_micro_recall = statistics.mean(list_micro_recall)
    cv_micro_recall_std = statistics.stdev(list_micro_recall)
    cv_micro_recall_min = min(list_micro_recall)
    cv_micro_recall_max = max(list_micro_recall)

    cv_micro_f1 = statistics.mean(list_micro_f1)
    cv_micro_f1_std = statistics.stdev(list_micro_f1)
    cv_micro_f1_min = min(list_micro_f1)
    cv_micro_f1_max = max(list_micro_f1)

    cv_macro_precision = statistics.mean(list_macro_precision)
    cv_macro_precision_std = statistics.stdev(list_macro_precision)
    cv_macro_precision_min = min(list_macro_precision)
    cv_macro_precision_max = max(list_macro_precision)

    cv_macro_recall = statistics.mean(list_macro_recall)
    cv_macro_recall_std = statistics.stdev(list_macro_recall)
    cv_macro_recall_min = min(list_macro_recall)
    cv_macro_recall_max = max(list_macro_recall)

    cv_macro_f1 = statistics.mean(list_macro_f1)
    cv_macro_f1_std = statistics.stdev(list_macro_f1)
    cv_macro_f1_min = min(list_macro_f1)
    cv_macro_f1_max = max(list_macro_f1)

    cv_weighted_precision = statistics.mean(list_weighted_precision)
    cv_weighted_precision_std = statistics.stdev(list_weighted_precision)
    cv_weighted_precision_min = min(list_weighted_precision)
    cv_weighted_precision_max = max(list_weighted_precision)

    cv_weighted_recall = statistics.mean(list_weighted_recall)
    cv_weighted_recall_std = statistics.stdev(list_weighted_recall)
    cv_weighted_recall_min = min(list_weighted_recall)
    cv_weighted_recall_max = max(list_weighted_recall)

    cv_weighted_f1 = statistics.mean(list_weighted_f1)
    cv_weighted_f1_std = statistics.stdev(list_weighted_f1)
    cv_weighted_f1_min = min(list_weighted_f1)
    cv_weighted_f1_max = max(list_weighted_f1)

    cv_macro_roc_auc_ovo = statistics.mean(list_macro_roc_auc_ovo)
    cv_macro_roc_auc_ovo_std = statistics.stdev(list_macro_roc_auc_ovo)
    cv_macro_roc_auc_ovo_min = min(list_macro_roc_auc_ovo)
    cv_macro_roc_auc_ovo_max = max(list_macro_roc_auc_ovo)

    cv_weighted_roc_auc_ovo = statistics.mean(list_weighted_roc_auc_ovo)
    cv_weighted_roc_auc_ovo_std = statistics.stdev(list_weighted_roc_auc_ovo)
    cv_weighted_roc_auc_ovo_min = min(list_weighted_roc_auc_ovo)
    cv_weighted_roc_auc_ovo_max = max(list_weighted_roc_auc_ovo)

    cv_macro_roc_auc_ovr = statistics.mean(list_macro_roc_auc_ovr)
    cv_macro_roc_auc_ovr_std = statistics.stdev(list_macro_roc_auc_ovr)
    cv_macro_roc_auc_ovr_min = min(list_macro_roc_auc_ovr)
    cv_macro_roc_auc_ovr_max = max(list_macro_roc_auc_ovr)

    cv_weighted_roc_auc_ovr = statistics.mean(list_weighted_roc_auc_ovr)
    cv_weighted_roc_auc_ovr_std = statistics.stdev(list_weighted_roc_auc_ovr)
    cv_weighted_roc_auc_ovr_min = min(list_weighted_roc_auc_ovr)
    cv_weighted_roc_auc_ovr_max = max(list_weighted_roc_auc_ovr)

    tab1_res = list()
    # ==========================
    res_acc = ["Accuracy",
               cv_accuracy,
               (cv_accuracy_std * 2),
               cv_accuracy_min,
               cv_accuracy_max,
               len(list_results),
               ]
    tab1_res.append(res_acc)
    # ==========================
    res_micro_prec = ["micro_precision",
                      cv_micro_precision,
                      (cv_micro_precision_std * 2),
                      cv_micro_precision_min,
                      cv_micro_precision_max,
                      len(list_results),
                      ]
    tab1_res.append(res_micro_prec)

    res_micro_recall = ["micro_recall",
                        cv_micro_recall,
                        (cv_micro_recall_std * 2),
                        cv_micro_recall_min,
                        cv_micro_recall_max,
                        len(list_results),
                        ]
    tab1_res.append(res_micro_recall)

    res_micro_f1 = ["micro_f1",
                    cv_micro_f1,
                    (cv_micro_f1_std * 2),
                    cv_micro_f1_min,
                    cv_micro_f1_max,
                    len(list_results),
                    ]
    tab1_res.append(res_micro_f1)
    # ==========================
    res_macro_prec = ["macro_precision",
                      cv_macro_precision,
                      (cv_macro_precision_std * 2),
                      cv_macro_precision_min,
                      cv_macro_precision_max,
                      len(list_results),
                      ]
    tab1_res.append(res_macro_prec)

    res_macro_recall = ["macro_recall",
                        cv_macro_recall,
                        (cv_macro_recall_std * 2),
                        cv_macro_recall_min,
                        cv_macro_recall_max,
                        len(list_results),
                        ]
    tab1_res.append(res_macro_recall)

    res_macro_f1 = ["macro_f1",
                    cv_macro_f1,
                    (cv_macro_f1_std * 2),
                    cv_macro_f1_min,
                    cv_macro_f1_max,
                    len(list_results),
                    ]
    tab1_res.append(res_macro_f1)
    # ==========================
    res_weighted_prec = ["weighted_precision",
                         cv_weighted_precision,
                         (cv_weighted_precision_std * 2),
                         cv_weighted_precision_min,
                         cv_weighted_precision_max,
                         len(list_results),
                         ]
    tab1_res.append(res_weighted_prec)

    res_weighted_recall = ["weighted_recall",
                           cv_weighted_recall,
                           (cv_weighted_recall_std * 2),
                           cv_weighted_recall_min,
                           cv_weighted_recall_max,
                           len(list_results),
                           ]
    tab1_res.append(res_weighted_recall)

    res_weighted_f1 = ["weighted_f1",
                       cv_weighted_f1,
                       (cv_weighted_f1_std * 2),
                       cv_weighted_f1_min,
                       cv_weighted_f1_max,
                       len(list_results),
                       ]
    tab1_res.append(res_weighted_f1)
    # ==========================
    res_macro_roc_auc_ovo = ["One-vs-One ROC AUC",
                             cv_macro_roc_auc_ovo,
                             (cv_macro_roc_auc_ovo_std * 2),
                             cv_macro_roc_auc_ovo_min,
                             cv_macro_roc_auc_ovo_max,
                             len(list_results),
                             ]
    tab1_res.append(res_macro_roc_auc_ovo)

    res_weighted_roc_auc_ovo = ["One-vs-One ROC AUC weighted",
                                cv_weighted_roc_auc_ovo,
                                (cv_weighted_roc_auc_ovo_std * 2),
                                cv_weighted_roc_auc_ovo_min,
                                cv_weighted_roc_auc_ovo_max,
                                len(list_results),
                                ]
    tab1_res.append(res_weighted_roc_auc_ovo)

    res_macro_roc_auc_ovr = ["One-vs-Rest ROC AUC",
                             cv_macro_roc_auc_ovr,
                             (cv_macro_roc_auc_ovr_std * 2),
                             cv_macro_roc_auc_ovr_min,
                             cv_macro_roc_auc_ovr_max,
                             len(list_results),
                             ]
    tab1_res.append(res_macro_roc_auc_ovr)

    res_weighted_roc_auc_ovr = ["One-vs-Rest ROC AUC weighted",
                                cv_weighted_roc_auc_ovr,
                                (cv_weighted_roc_auc_ovr_std * 2),
                                cv_weighted_roc_auc_ovr_min,
                                cv_weighted_roc_auc_ovr_max,
                                len(list_results),
                                ]
    tab1_res.append(res_weighted_roc_auc_ovr)
    # ==========================

    return (tab1_res)


def get_results(model_fit, named_features, importance_minval, test_XX, train_yy, test_yy):
    y_pred = model_fit.predict(test_XX)
    y_prob = model_fit.predict_proba(test_XX)

    conf_matrix = metrics.confusion_matrix(test_yy, y_pred)

    acc = metrics.accuracy_score(test_yy, y_pred)

    micro_precision = metrics.precision_score(test_yy, y_pred, average='micro')
    micro_recall = metrics.recall_score(test_yy, y_pred, average='micro')
    micro_f1 = metrics.f1_score(test_yy, y_pred, average='micro')

    macro_precision = metrics.precision_score(test_yy, y_pred, average='macro')
    macro_recall = metrics.recall_score(test_yy, y_pred, average='macro')
    macro_f1 = metrics.f1_score(test_yy, y_pred, average='macro')

    weighted_precision = metrics.precision_score(test_yy, y_pred, average='weighted')
    weighted_recall = metrics.recall_score(test_yy, y_pred, average='weighted')
    weighted_f1 = metrics.f1_score(test_yy, y_pred, average='weighted')

    # should have SAME shape
    shape_y_test = test_yy.shape[0]
    shape_y_prob = y_prob.shape[1]
    valid = False
    if shape_y_test == shape_y_prob:
        # should have SAME amount of UNIQUE CLASSES
        class_test = len(np.unique(test_yy))
        if class_test == shape_y_prob:
            valid = True

    if valid == True:
        macro_roc_auc_ovo = metrics.roc_auc_score(test_yy,
                                                  y_prob,
                                                  multi_class="ovo",
                                                  average="macro")

        weighted_roc_auc_ovo = metrics.roc_auc_score(test_yy,
                                                     y_prob,
                                                     multi_class="ovo",
                                                     average="weighted")

        macro_roc_auc_ovr = metrics.roc_auc_score(test_yy,
                                                  y_prob,
                                                  multi_class="ovr",
                                                  average="macro")

        weighted_roc_auc_ovr = metrics.roc_auc_score(test_yy,
                                                     y_prob,
                                                     multi_class="ovr",
                                                     average="weighted")
    else:
        print("WARNING: Number of classes in y_prob not equal to the number of columns in 'y_test'")
        macro_roc_auc_ovo = 0
        weighted_roc_auc_ovo = 0
        macro_roc_auc_ovr = 0
        weighted_roc_auc_ovr = 0

    # Print features by importance

    feature_imp = pd.Series(model_fit.feature_importances_,
                            index=named_features).sort_values(ascending=False)

    df_importance_1 = pd.DataFrame({'Feature': feature_imp.index, 'Value': feature_imp.values})

    # Feature selection 1
    # remove any feature that has an information gain (entropy) LESS than 0.005 (0.5%)
    if importance_minval == 0:
        excluded = list()
    else:
        excluded = df_importance_1[df_importance_1['Value'] <= importance_minval]
        excluded = list(excluded.iloc[:, 0])

    importances = model_fit.feature_importances_

    importances_std = np.std([tree.feature_importances_ for tree in model_fit.estimators_], axis=0)

    modres = [
        acc,
        model_fit,
        micro_precision,
        micro_recall,
        micro_f1,
        macro_precision,
        macro_recall,
        macro_f1,
        weighted_precision,
        weighted_recall,
        weighted_f1,

        macro_roc_auc_ovo,
        weighted_roc_auc_ovo,
        macro_roc_auc_ovr,
        weighted_roc_auc_ovr,

        importances,
        importances_std,
        conf_matrix,

        feature_imp.to_dict(),
        df_importance_1,
        excluded,

    ]
    return (modres)


def plot_confusion_matrix(confusion_matrix_data, name_classes):

    # Build the plot
    plt.figure(figsize=(16, 7))
    sns.set(font_scale=1.4)
    sns.heatmap(confusion_matrix_data,
                annot=True,
                annot_kws={'size': 10},
                cmap=plt.cm.Greens,
                linewidths=0.2)

    # Add labels to the plot
    tick_marks = np.arange(len(name_classes))
    tick_marks2 = tick_marks + 0.5
    plt.xticks(tick_marks, name_classes, rotation=25)
    plt.yticks(tick_marks2, name_classes, rotation=0)
    plt.xlabel('Predicted label')
    plt.ylabel('True label')
    plt.title('Confusion Matrix for Random Forest Model')
    plot_name = current_dir + feature + '_confusion_matrix.png'
    plt.savefig(plot_name)
    # plt.show()


def manual_CV_RF(original_data,
                 data_x, data_y,
                 sampling,
                 num_folds=5,
                 plot_conf=False,
                 print_imp=True,
                 min_ig_val=0.0001):
    print("DATASET SHAPE -> %s x %s" % (len(data_x), len(data_y)))

    cross_tab = pd.crosstab(data_y, 'count')

    max_freq = int(cross_tab.max().values)
    print("MAX FREQUENCY FOUND -> ", max_freq)

    all_classes = np.unique(data_y)
    print("TOT CLASSES FOUND -> ", len(all_classes))

    # int, to specify the number of folds in a (Stratified)KFold
    print("FOLDS REQUESTED -> ", num_folds)
    if max_freq < num_folds:
        num_folds = max_freq
    print("FOLDS POSSIBLE -> ", num_folds)

    print("MINIMUM IG requested -> ", min_ig_val)

    results = dict()
    count = 0
    top_step = 0
    top_acc = 0

    feature_names = list(data_x.columns)

    if sampling == "ShuffleSplit":

        # macro-average
        # compute the metric independently for each class and then take the average
        # micro-average
        # will aggregate the contributions of all classes to compute the average metric
        # NOTE -> In a multi-class classification setup,
        #         micro-average is preferable if you suspect there might be class imbalance

        for nn in range(0, num_folds):

            print("RUNNING MODEL ->", count)
            # https://stackoverflow.com/questions/34842405/parameter-stratify-from-method-train-test-split-scikit-learn
            X_train, X_test, y_train, y_test = train_test_split(data_x,
                                                                data_y,
                                                                test_size=0.25,
                                                                random_state=42,
                                                                stratify=data_y,
                                                                )

            # USING WEKA defaults
            # criterion -> entropy
            # number of folds -> 3
            # minimum variance for split -> 1e-3
            # size of each bag -> 100
            # number of trees -> 100
            # number attributes -> 0 for unlimited
            # number of instances per leaf -> 2
            raf = RandomForestClassifier(n_estimators=100,
                                         n_jobs=1,
                                         max_depth=None,
                                         min_samples_split=2,
                                         min_samples_leaf=1,
                                         bootstrap=True,
                                         oob_score=True,  # Out of bag estimation only available if bootstrap=True"
                                         # bootstrap = False,
                                         max_features='log2',
                                         max_leaf_nodes=None,
                                         min_impurity_decrease=0.0,
                                         warm_start=False,
                                         # criterion = 'gini', # Gini impurity
                                         criterion='entropy',  # Information gain
                                         )

            raf.fit(X_train, y_train)

            model_intra_results = get_results(raf, feature_names, min_ig_val, X_test, y_train, y_test)

            if model_intra_results[0] > top_acc:
                top_acc = model_intra_results[0]
                top_step = count

            # put results in dict
            results[count] = model_intra_results
            print(feature_names)
            count = count + 1
    else:

        if sampling == "StratifiedKFold":
            splm = StratifiedKFold(n_splits=num_folds,
                                   shuffle=True,
                                   random_state=42)

        elif sampling == "StratifiedShuffleSplit":
            splm = StratifiedShuffleSplit(n_splits=num_folds,
                                          test_size=0.25,
                                          random_state=42)

        elif sampling == "KFold":
            splm = KFold(n_splits=num_folds,
                         shuffle=True,
                         random_state=42)

        else:
            raise AssertionError("ERROR: sampling mode unknown")

        for train_index, test_index in splm.split(np.zeros(len(data_x)), data_y):
            X_train, X_test = data_x.iloc[train_index], data_x.iloc[test_index]
            y_train, y_test = data_y[train_index], data_y[test_index]

            print("RUNNING MODEL ->", count)
            # USING WEKA defaults
            # criterion -> entropy
            # number of folds -> 3
            # minimum variance for split -> 1e-3
            # size of each bag -> 100
            # number of trees -> 100
            # number attributes -> 0 for unlimited
            # number of instances per leaf -> 2
            raf = RandomForestClassifier(n_estimators=100,
                                         n_jobs=1,
                                         max_depth=None,
                                         min_samples_split=2,
                                         min_samples_leaf=1,
                                         bootstrap=True,
                                         oob_score=True,  # Out of bag estimation only available if bootstrap=True"
                                         # bootstrap = False,
                                         max_features='log2',
                                         max_leaf_nodes=None,
                                         min_impurity_decrease=0.0,
                                         warm_start=False,
                                         # criterion = 'gini', # Gini impurity
                                         criterion='entropy',  # Information gain
                                         )

            raf.fit(X_train, y_train)

            model_intra_results = get_results(raf, feature_names, min_ig_val, X_test, y_train, y_test)

            if model_intra_results[0] > top_acc:
                top_acc = model_intra_results[0]
                top_step = count

            # put results in dict
            results[count] = model_intra_results

            count = count + 1

    temp_dict = OrderedDict()

    top_model_features = results[top_step]
    for k, v in top_model_features[18].items():
        temp_dict[k] = v
    sorted_x = sorted(temp_dict.items(), key=operator.itemgetter(1), reverse=True)
    sorted_dict = OrderedDict(sorted_x)

    feat_dict_top = OrderedDict()
    for k, v in sorted_dict.items():
        feat_dict_top[k] = v

    feat_dict_all = OrderedDict()
    for x in range(0, 5):
        for k, v in results[x][18].items():
            if not k in feat_dict_all:
                feat_dict_all[k] = [v]
            else:
                feat_dict_all[k].append(v)

    feat_dict_final = OrderedDict()
    for k, v in feat_dict_top.items():
        feat_dict_final[k] = dict()
        feat_dict_final[k]["top"] = v
        feat_dict_final[k]["accs"] = list()
        feat_dict_final[k]["cv_acc"] = 0
        feat_dict_final[k]["stdev"] = 0
        feat_dict_final[k]["cv_min"] = 0
        feat_dict_final[k]["cv_max"] = 0
        feat_dict_final[k]["keep"] = False

    for k, v in feat_dict_all.items():
        if not k in feat_dict_final:
            feat_dict_final[k]["accs"] = list()
            for item in v:
                feat_dict_final[k]["accs"].append(item)
        else:
            feat_dict_final[k]["accs"] = v

    feat_keep = list()
    feat_drop = list()
    for k, v in feat_dict_final.items():
        feat_dict_final[k]["cv_acc"] = statistics.mean(v["accs"])
        feat_dict_final[k]["stdev"] = statistics.stdev(v["accs"]) * 2
        feat_dict_final[k]["cv_min"] = min(v["accs"])
        feat_dict_final[k]["cv_max"] = max(v["accs"])
        if min(v["accs"]) >= min_ig_val:
            feat_dict_final[k]["keep"] = True
            feat_keep.append(k)
        else:
            feat_drop.append(k)

    with open("top_model_feature_stats.json", "w") as outfile:
        json.dump(feat_dict_final, outfile)
    table_head = ["Feature", "Top Accuracy", "CV.Acc", "+/- 2*Std.", "CV.Min", "CV.Max", "Decision"]

    final_list = list()
    for k, v in feat_dict_final.items():
        mid_list = [
            k,
            v["top"],
            v["cv_acc"],
            v["stdev"],
            v["cv_min"],
            v["cv_max"],
            v["keep"],
        ]
        final_list.append(mid_list)

    # ==========================

    print("SAMPLING -> ", sampling)
    print("TOTAL folds -> ", num_folds)
    print("TOTAL rounds -> ", len(results))
    print("BEST MODEL - round -> ", top_step)
    print("BEST MODEL - accuracy -> ", top_acc)

    # ==========================

    print()
    tab1_head = ["Value", "CV.Acc", "+/- 2*Std.", "CV.Min", "CV.Max", "Runs"]
    results_prepared = prepare_results(results)
    cv_res_tabs = tabulate(results_prepared, tab1_head, tablefmt="github")

    print(cv_res_tabs)
    print()
    # ==========================

    # Get the confusion matrix
    cm = results[top_step][17]

    # We will store the results in a dictionary for easy access later
    per_class_accuracies = {}

    # Calculate the accuracy for each one of our classes
    for idx, cls in enumerate(all_classes):
        # True negatives are all the samples that are not our current GT class (not the current row)
        # and were not predicted as the current class (not the current column)
        true_negatives = np.sum(np.delete(np.delete(cm, idx, axis=0), idx, axis=1))

        # True positives are all the samples of our current GT class that were predicted as such
        true_positives = cm[idx, idx]

        # The accuracy for the current class is ratio between correct predictions to all predictions
        per_class_accuracies[cls] = (true_positives + true_negatives) / np.sum(cm)

    tab_res = list()
    tab_headers = ['Class', 'Accuracy', ]
    for k, v in per_class_accuracies.items():
        tab_res.append([k, v])
    with open(class_accuracy_output, 'w') as f:
        f.write(tabulate(tab_res, tab_headers, tablefmt="rst"))
    f.close()

    if plot_conf == True:
        plot_confusion_matrix(results[top_step][17], all_classes)

    # ==========================

    if min_ig_val > 0:
        print("Features to be excluded because of low importance")

        tot_fc = len(feature_names)
        print("TOTAL FEATURES - -> %s " % (tot_fc,))

        to_exc_list = feat_drop
        tot_exc = len(to_exc_list)
        tot_exc_p = (tot_exc / tot_fc) * 100

        tot_fc_rem = tot_fc - tot_exc
        tot_fc_rem_p = (tot_fc_rem / tot_fc) * 100

        print("TOTAL FEATURES - TO BE EXCLUDED -> %s (%s %%)" % (tot_exc, tot_exc_p))
        print("TOTAL FEATURES - REMAINING -> %s (%s %%)" % (tot_fc_rem, tot_fc_rem_p))

        newset = original_data.copy()
        for item in to_exc_list:
            newset = newset.drop(item, axis=1)
        print("PRODUCING DATASET - IG FILTERED SHAPE -> ", newset.shape)

        newset.to_csv("dataset_IG_cleaned_005.csv", index=False)

    # ==========================

    if print_imp == True:
        print()
        print("Features by importance (descending)")

        res_feat_imp_des = results[top_step][19]
        res_feat_top_3 = res_feat_imp_des['Value'].head(3).sum()
        print("FEATURES - SUM Accuracy TOP 3 -> ", res_feat_top_3)

        res_feat_top_5 = res_feat_imp_des['Value'].head(5).sum()
        print("FEATURES - SUM Accuracy TOP 5 -> ", res_feat_top_5)

        if len(res_feat_imp_des) > 9:
            res_feat_top_10 = res_feat_imp_des['Value'].head(10).sum()
            print("FEATURES - SUM Accuracy TOP 10 -> ", res_feat_top_10)

        if len(res_feat_imp_des) > 14:
            res_feat_top_15 = res_feat_imp_des['Value'].head(15).sum()
            print("FEATURES - SUM Accuracy TOP 15 -> ", res_feat_top_15)

        if len(res_feat_imp_des) > 19:
            res_feat_top_20 = res_feat_imp_des['Value'].head(20).sum()
            print("FEATURES - SUM Accuracy TOP 20 -> ", res_feat_top_20)

        if len(res_feat_imp_des) > 24:
            res_feat_top_25 = res_feat_imp_des['Value'].head(25).sum()
            print("FEATURES - SUM Accuracy TOP 25 -> ", res_feat_top_25)

        print()
        feat_to_10 = 0
        feat_to_20 = 0
        feat_to_30 = 0
        feat_to_40 = 0
        feat_to_50 = 0
        feat_to_60 = 0
        feat_to_70 = 0
        feat_to_80 = 0
        feat_to_90 = 0
        feat_to_95 = 0
        feat_to_99 = 0

        feat_sums = dict()
        fcount = 1
        feat_sum = 0
        for xft in res_feat_imp_des['Value'].tolist():
            feat_sum = feat_sum + xft
            if xft > 0:
                if feat_sum <= 0.10:
                    feat_to_10 = fcount
                elif feat_sum <= 0.20:
                    feat_to_20 = fcount
                elif feat_sum <= 0.30:
                    feat_to_30 = fcount
                elif feat_sum <= 0.40:
                    feat_to_40 = fcount
                elif feat_sum <= 0.50:
                    feat_to_50 = fcount
                elif feat_sum <= 0.60:
                    feat_to_60 = fcount
                elif feat_sum <= 0.70:
                    feat_to_70 = fcount
                elif feat_sum <= 0.80:
                    feat_to_80 = fcount
                elif feat_sum <= 0.90:
                    feat_to_90 = fcount
                elif feat_sum <= 0.95:
                    feat_to_95 = fcount
                elif feat_sum <= 0.99:
                    feat_to_99 = fcount
                feat_sums[fcount] = feat_sum * 100
                fcount = fcount + 1
        print("Number of features needed to achieve target Accuracy")
        print("FEATURES - Features to reach 10% -> ", feat_to_10)
        print("FEATURES - Features to reach 20% -> ", feat_to_20)
        print("FEATURES - Features to reach 30% -> ", feat_to_30)
        print("FEATURES - Features to reach 40% -> ", feat_to_40)
        print("FEATURES - Features to reach 50% -> ", feat_to_50)
        print("FEATURES - Features to reach 60% -> ", feat_to_60)
        print("FEATURES - Features to reach 70% -> ", feat_to_70)
        print("FEATURES - Features to reach 80% -> ", feat_to_80)
        print("FEATURES - Features to reach 90% -> ", feat_to_90)
        print("FEATURES - Features to reach 95% -> ", feat_to_95)
        print("FEATURES - Features to reach 99% -> ", feat_to_99)

        print(results[top_step][19])

        feat_sum_lists = sorted(feat_sums.items())  # sorted by key, return a list of tuples
        x, y = zip(*feat_sum_lists)  # unpack a list of pairs into two tuples
        plt.figure()
        plt.plot(x, y)
        plot_title = current_dir + feature + '_features_plot.png'
        plt.savefig(plot_title)
        #plt.show()

    # ==========================

    print("========================")
    print(results_prepared)
    print("========================")

def present_results(data_type, mod_results):
    tab_headers = ['Model', 'CV.Acc.', '+/- 2*Std.', 'Folds', 'CV.Min', 'CV.Max', 'Elapsed', ]
    acc_tabs = tabulate(mod_results, tab_headers, tablefmt="rst")
    with open(class_accuracy_output, 'a') as f:
        f.write("\n")
        f.write(acc_tabs)
    f.close()

def cross_validation(classifier, data_x, data_y):
    cross_tab = pd.crosstab(data_y, 'count')

    max_freq = int(cross_tab.max().values)

    # int, to specify the number of folds in a (Stratified)KFold
    s_kfolds = 5
    if max_freq < s_kfolds:
        s_kfolds = max_freq

    try:
        score = cross_val_score(classifier,
                                data_x,
                                y=data_y,
                                cv=s_kfolds)
        mean = score.mean()
        std = score.std() * 2
        xmin = score.min()
        xmax = score.max()
    except:
        mean = 'ERROR'
        std = 'ERROR'

    return [mean, std, s_kfolds, score, xmin, xmax]


man_results = manual_CV_RF(original,
                           features,
                           labels,
                           "StratifiedKFold",
                           num_folds=5,
                           plot_conf=True,
                           print_imp=True,
                           min_ig_val=0.0001,
                           )

print(man_results)

mod_results, mod_details = compute_models(features, labels,
                                          X_train, y_train,
                                          X_test, y_test)

present_results('STD', mod_results)