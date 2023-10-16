import io
import os, math
import argparse
from PIL import Image
from queue import Queue
from threading import Thread
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
import json

import urllib
import sys

main_folder = str(sys.argv[-1])
input_Dataset = main_folder

sally_out = input_Dataset + '.txt'
sally_parsed = input_Dataset + ".csv"
sally_parsed_top50 = input_Dataset + "-top50.csv"
Code_gram = input_Dataset + "_cg.csv"


def slidingWindow(sequence, winSize, step=1):
    """Returns a generator that will iterate through
    the defined chunks of input sequence.  Input sequence
    must be iterable."""

    temp = list()

    # Verify the inputs
    if not ((type(winSize) == type(0)) and (type(step) == type(0))):
        raise Exception("**ERROR** type(winSize) and type(step) must be int.")

    if step > winSize:
        raise Exception("**ERROR** step must not be larger than winSize.")

    if winSize > len(sequence):
        # raise Exception("**ERROR** winSize must not be larger than sequence length.")
        temp = []
    else:
        try:
            it = iter(sequence)
        except TypeError:
            raise Exception("**ERROR** sequence must be iterable.")

        # Pre-compute number of chunks to emit
        numOfChunks = int(((len(sequence) - winSize) / step) + 1)

        # Do the work
        for i in range(0, numOfChunks * step, step):
            temp.append(sequence[i:i + winSize])

    return (temp)


def getBinaryData(input_file, cgig):
    with io.open(input_file, "rb") as f:
        data = f.read()

    chunks = slidingWindow(data, 4)

    binary_values = []
    for chunk in chunks:

        encoded = urllib.parse.quote_plus(chunk)

        temp = list()
        for xx in chunk:
            nn = int(xx)
            temp.append(nn)

        if encoded in cgig:

            for item in temp:
                binary_values.append(item)

    return (binary_values)


def createGreyScaleImage(filename, cg, cgIG, width=None):
    """
    Create greyscale image from  data. Use given with if defined or create square size image from binary data.
    :param filename: image filename
    """

    greyscale_data = getBinaryData(filename, cgIG)

    size = get_size(len(greyscale_data), width)
    save_file(filename, greyscale_data, size, 'L', '_IGFilter_')


def save_file(filename, data, size, image_type, outFile):
    try:
        image = Image.new(image_type, size)
        image.putdata(data)

        # setup output filename
        dirname = os.path.dirname(filename)
        name, _ = os.path.splitext(filename)
        name = os.path.basename(name)
        imagename = dirname + os.sep + name + outFile + image_type + '.png'
        os.makedirs(os.path.dirname(imagename), exist_ok=True)
        image.save(imagename)

    except Exception as err:
        print(err)


def get_size(data_length, width=None):
    # source Malware images: visualization and automatic classification by L. Nataraj
    # url : http://dl.acm.org/citation.cfm?id=2016908

    if width is None:  # with don't specified any with value

        size = data_length

        if size < 10240:
            width = 32
        elif 10240 <= size <= 10240 * 3:
            width = 64
        elif 10240 * 3 <= size <= 10240 * 6:
            width = 128
        elif 10240 * 6 <= size <= 10240 * 10:
            width = 256
        elif 10240 * 10 <= size <= 10240 * 20:
            width = 384
        elif 10240 * 20 <= size <= 10240 * 50:
            width = 512
        elif 10240 * 50 <= size <= 10240 * 100:
            width = 768
        else:
            width = 1024

        height = int(size / width) + 1

    else:
        width = int(math.sqrt(data_length)) + 1
        height = width

    return width, height


def run(file_queue, cg, cgIG, width):
    while not file_queue.empty():
        filename = file_queue.get()
        createGreyScaleImage(filename, cg, cgIG, width)
        file_queue.task_done()


def main(input_Dataset, Code_gram, width=None, thread_number=7):
    cg = dict()
    cgListOrg = []
    cgListIG = []

    from urllib.parse import unquote
    file1 = open(Code_gram, 'r')
    Lines = file1.readlines()
    # Strips the newline character 
    for line in Lines:
        xline = line.replace("\n", "")
        cgListOrg.append(xline.split(",")[1])

    source_data = pd.read_csv(sally_parsed_top50)
    source_data[['Name', 'Extension']] = source_data.Filename.str.split(".", expand=True)
    source_data = source_data.dropna()
    print("Number of files: ", len(source_data), "\nNumber of features: ", len(source_data.columns))

    features = source_data
    features.fillna(0)
    features = features.dropna()

    print("Features Size", len(features.columns))
    print("languages", set(features.Extension))
    print("Number of Authors", len(set(features.Author)))
    print("Number of Files", len(features))

    if 'Author' in features:
        features["Author"] = features["Author"].astype('category')
        features["Author"] = features["Author"].cat.codes

    if 'Extension' in features:
        features = features.drop('Extension', axis=1)
    if 'Extension_x' in features:
        features = features.drop('Extension_x', axis=1)
    if 'Extension_y' in features:
        features = features.drop('Extension_y', axis=1)
    if 'FilePath' in features:
        features = features.drop('FilePath', axis=1)
    if 'Basename' in features:
        features = features.drop('Basename', axis=1)
    if 'Confidence' in features:
        features = features.drop('Confidence', axis=1)
    if 'Encoding' in features:
        features = features.drop('Encoding', axis=1)

    if 'Name' in features:
        features = features.drop('Name', axis=1)
    if 'fullpath' in features:
        features = features.drop('fullpath', axis=1)
    if 'Group' in features:
        features = features.drop('Group', axis=1)
    if 'Filename' in features:
        features = features.drop('Filename', axis=1)

    labels = np.array(features['Author'])

    if 'Author' in features:
        features = features.drop('Author', axis=1)

    print("-----------------------------------IG----------------------------")

    # Saving feature names for later use
    feature_list5 = list(features.columns)

    rf_ig_model = RandomForestClassifier(n_estimators=100,
                                         n_jobs=5,
                                         max_depth=None,
                                         min_samples_split=2,
                                         min_samples_leaf=1,
                                         bootstrap=False,
                                         oob_score=False,  # Out of bag estimation only available if bootstrap=True"
                                         # bootstrap = False,
                                         max_features='auto',
                                         max_leaf_nodes=None,
                                         min_impurity_decrease=0.0,
                                         warm_start=False,
                                         criterion='entropy',  # Gini impurity
                                         # criterion = 'entropy', # Information gain
                                         )

    # -------------------------------------------------------------------------
    # Split the data into training and testing sets

    X_train, X_test, y_train, y_test = train_test_split(features,
                                                        labels,
                                                        test_size=0.25,
                                                        random_state=42)

    # -------------------------------------------------------------------------

    rf_ig_model.fit(X_train, y_train)
    y_pred_test = rf_ig_model.predict(X_test)

    print(classification_report(y_test, y_pred_test))

    # -------------------------------------------------------------------------

    # Print features by importance
    feature_imp = pd.Series(rf_ig_model.feature_importances_,
                            index=feature_list5).sort_values(ascending=False)

    df_importance_1 = pd.DataFrame({'Feature': feature_imp.index, 'Value': feature_imp.values})

    # Feature selection 1
    # remove any feature that has an information gain (entropy) LESS than 0.01

    importance_minval = 0.01

    excluded = df_importance_1[df_importance_1['Value'] <= importance_minval]

    excluded = list(excluded.iloc[:, 0])

    for item in excluded:
        features = features.drop(item, axis=1)

    for line in Lines:
        xline = line.strip().replace("\n", "")
        if unquote(xline.split(",")[0]) in features.columns:
            cgListIG.append(xline.split(",")[1])

    file_queue = Queue()
    for root, directories, files in os.walk(input_Dataset):
        for filename in files:
            file_path = os.path.join(root, filename)
            if not file_path.endswith(".png"):
                file_queue.put(file_path)

    # Start thread
    for index in range(thread_number):
        thread = Thread(target=run, args=(file_queue, cgListOrg, cgListIG, width))
        thread.daemon = True
        thread.start()
    file_queue.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='2_input2Image.py', description="Convert binary file to image")
    parser.add_argument(dest='input_Dataset', help='Input directory path is which include executable files')

    main(input_Dataset, Code_gram, width=None)

sys.exit()
