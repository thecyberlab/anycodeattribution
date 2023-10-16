#!/usr/bin/env python
# -*- coding: utf-8 -*-


# This code allows to extract Kothari et al. features (described in Kothari et al. study https://ieeexplore.ieee.org/document/4151691) from source code files.
# The main output file is kothari.arff, which contains Kothari et al. feature vectors.

# This code should be located in the same folder as input files and can be executed by any Python IDEs.


import io
import sys
import os
import os.path
from collections import Counter
from collections import OrderedDict
import base64
import operator
import time
from datetime import timedelta
import json


# ==============================================================================


def absoluteFilePaths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def string_chunks(input_string, chunk_size):
    chunk_size = int(chunk_size)
    result = [input_string[i:i + chunk_size] for i in range(0, len(input_string), chunk_size)]
    return (result)


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
        for i in range(0, numOfChunks * step, step):
            temp.append(sequence[i:i + winSize])

    return (temp)


# ==============================================================================

# Get the directory of the script being executed
script_directory = os.path.dirname(os.path.abspath(__file__))
config_path = script_directory + "/kothari_config.json"

# Read JSON file
with io.open(config_path, 'r') as rcf:
    kothari_config = json.load(rcf)

main_directory = str(sys.argv[-1])
separator = kothari_config["separator"]
error_file = script_directory + "/kothari_errors.txt"
valid_grams = main_directory + separator + kothari_config["valid_grams"]
temp_file = main_directory + separator + kothari_config["temp_file"]
total_frequencies = main_directory + separator + kothari_config["total_frequencies"]
result_file_0 = main_directory + separator + kothari_config["result_file_0"]
result_file_a = main_directory + separator + kothari_config["result_file_a"]
result_file_e = main_directory + separator + kothari_config["result_file_e"]
result_file_i = main_directory + separator + kothari_config["result_file_i"]
result_file_m = main_directory + separator + kothari_config["result_file_m"]
result_file_q = main_directory + separator + kothari_config["result_file_q"]
result_file_u = main_directory + separator + kothari_config["result_file_u"]
result_file_y = main_directory + separator + kothari_config["result_file_y"]
extension = kothari_config["extension"]

with io.open(error_file, 'w') as wfg:
    wfg.write("")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 


def get_file_data_flat(file_path):
    temp_data = list()
    with io.open(file_path, 'r', encoding="utf-8", errors='ignore') as rfl:
        for line in rfl:
            temp_data.append(line)

    # join all lines (flatten file to 1 string)
    flat = ''.join(temp_data)
    data = flat.replace("\r\n", "").replace("\r", "").replace("\n", "")

    return (data)


def get_all_author_grams(list_of_files):
    xgram_files = list()
    xjava_files = list()
    for xitem in list_of_files:
        if not ("/._" in xitem):
            if xitem.endswith(extension):
                if not (xitem in xjava_files):
                    xjava_files.append(xitem)
            elif xitem.endswith(".4grams"):
                if not (xitem in xgram_files):
                    xgram_files.append(xitem)
    xjava_files.sort()
    xgram_files.sort()

    # get all unique 4grams across ALL files PER SINGLE AUTHOR
    author_grams = list()
    for item in xjava_files:
        gramname = item.replace("\n", "").rstrip(extension) + ".4grams"
        if gramname in xgram_files:

            with io.open(gramname, 'r') as rgf:
                for aa in rgf:
                    xitem = aa.replace("\n", "")
                    author_grams.append(xitem)

    result = list(set(author_grams))
    return (result)


def get_all_author_grams_freq(list_of_files):
    ygram_files = list()
    yjava_files = list()
    for xitem in list_of_files:
        if not ("/._" in xitem):
            if xitem.endswith(extension):
                if not (xitem in yjava_files):
                    yjava_files.append(xitem)
            elif xitem.endswith(".4gramsf"):
                if not (xitem in ygram_files):
                    ygram_files.append(xitem)
    yjava_files.sort()
    ygram_files.sort()

    # get all unique 4grams FREQUENCIES across ALL files PER SINGLE AUTHOR
    author_grams_freq = dict()
    for item in yjava_files:
        gramname = item.replace("\n", "").rstrip(extension) + ".4gramsf"
        if gramname in ygram_files:

            with io.open(gramname, 'r') as rgf:
                for line in rgf:
                    xitem = line.replace("\n", "")
                    gram_code = xitem.split(",")[0].strip()
                    gram_count = int(xitem.split(",")[1].strip())

                    if gram_code in author_grams_freq:
                        author_grams_freq[gram_code] = author_grams_freq[gram_code] + gram_count
                    else:
                        author_grams_freq[gram_code] = gram_count

    sorted_fr = sorted(author_grams_freq.items(), key=operator.itemgetter(1))
    od_sorted_fr = OrderedDict(sorted_fr)
    return (od_sorted_fr)


def human_elapsed(epoch_time):
    res = str(timedelta(seconds=epoch_time))
    return (res)


file_time_step1 = OrderedDict()
file_time_step2 = OrderedDict()
file_time_step5 = OrderedDict()
file_time_step6 = OrderedDict()
file_time_step7 = OrderedDict()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# GET FILE LIST

timing0_start = time.time()

all_files = absoluteFilePaths(main_directory)

# list JAVA files
java_files = list()

# list AUTHORS
authors_path = list()
author_files = OrderedDict()

for item in all_files:
    if not ("/._" in item):
        if item.endswith(extension):

            java_files.append(item)
            author = item.replace(main_directory, "").split("/")[1]
            author_path = main_directory + "/" + author + "/"

            authors_path.append(author_path)

            if not author in author_files:
                author_files[author] = [item]
            else:
                author_files[author].append(item)

if not author_files:
    raise AssertionError("ERROR - no file have been found with the given extension")

java_files = list(set(java_files))
java_files.sort()

authors_path = list(set(authors_path))
authors_path.sort()

timing0_end = time.time()
timing0_elapsed = round((timing0_end - timing0_start), 8)

print()
print("Total AUTHORS found: %s" % (len(authors_path),))
print("Total files found: %s" % (len(java_files),))
print()
print("DONE -1- List files: '%s' - '%s'" % (timing0_elapsed, human_elapsed(timing0_elapsed),))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 
# COMPUTE 4grams PER EACH FILE


timing1_start = time.time()

if not author_files:
    raise AssertionError("ERROR - expected file list is empty")

# FOR JAVA FILE, get all lines with UTF-8 encoding
for author, file_list in author_files.items():

    java_files = list(set(file_list))
    java_files.sort()

    for java_file in java_files:

        gram_path = java_file[:-len(extension)] + ".4gramsf"

        flat_data = get_file_data_flat(java_file)

        if (len(flat_data) > 3):
            chunks = slidingWindow(flat_data, 4)

            if not chunks:
                print(java_file)
                print(repr(flat_data))
                print(chunks)
                raise AssertionError("ERROR - chunks list is empty")

            count_grams = OrderedDict(Counter(chunks))

            with io.open(gram_path, 'w') as wfg:
                for k, v in count_grams.items():
                    encoded = str(base64.urlsafe_b64encode(k.encode("utf8")))[2:-1]
                    item = "%s,%s\n" % (encoded, v)
                    wfg.write(item)

            if not os.path.exists(gram_path):
                print("MISSING FILE: ", gram_path)
                raise AssertionError("ERROR: expected file is has not been written to disk")

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        else:
            print("ERROR: 'flat_data' < 4 | ", java_file)

            with io.open(gram_path, 'w') as wfg:
                wfg.write("")

        java_files = None
        gram_path = None
        flat_data = None
        chunks = None
        count_grams = None

del (java_files)
del (gram_path)
del (flat_data)
del (chunks)
del (count_grams)

timing1_end = time.time()
timing1_elapsed = round((timing1_end - timing1_start), 8)
print("DONE -1- Save-files-4grams: '%s' - '%s'" % (timing1_elapsed, human_elapsed(timing1_elapsed),))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# READ all computed files, and find which developer has which ngram


timing2_start = time.time()

# process files PER AUTHOR
for author, file_list in author_files.items():

    author_path = main_directory + "/" + author + "/"
    author_freq_file = author_path + author + ".a4gramsf"

    xall_files = absoluteFilePaths(author_path)

    java_files = list()
    gramsf_files = list()
    for xitem in xall_files:
        if not ("/._" in xitem):
            if xitem.endswith(extension):
                java_files.append(xitem)
            elif xitem.endswith(".4gramsf"):
                gramsf_files.append(xitem)
    java_files = list(set(java_files))
    gramsf_files = list(set(gramsf_files))
    java_files.sort()
    gramsf_files.sort()

    if not (len(gramsf_files) == len(java_files)):
        print("Author: ", author)
        print("Number %s files %s: " % (extension, len(java_files)))
        print("Number .4gramsf files ", len(gramsf_files))

        miss = list()
        for xx in java_files:
            gram_file = xx[:-len(extension)] + ".4gramsf"

            if not gram_file in gramsf_files:
                miss.append(gram_file)

        print("Missing: ", miss)
        raise AssertionError("Number authors not equal number author files")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    # get all unique 4grams FREQUENCIES across ALL files PER SINGLE AUTHOR
    author_grams_freq = OrderedDict()

    for item in gramsf_files:

        if os.path.isfile(item):

            with io.open(item, 'r') as rgf:
                for line in rgf:
                    if line:
                        yitem = line.replace("\n", "")
                        gram_code = yitem.split(",")[0].strip()
                        gram_count = int(yitem.split(",")[1].strip())

                        if gram_code in author_grams_freq:
                            author_grams_freq[gram_code] = author_grams_freq[gram_code] + gram_count
                        else:
                            author_grams_freq[gram_code] = gram_count
        else:
            print("Missing file: ", item)
            raise AssertionError("Number authors not equal number author files")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    with io.open(author_freq_file, 'w') as wgf:
        for k, v in author_grams_freq.items():
            xxx = "%s,%s\n" % (k, v)
            wgf.write(xxx)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    author = None
    author_path = None
    author_freq_file = None
    gramsf_files = None
    xall_files = None
    java_files = None
    gramsf_files = None
    xitem = None
    xx = None
    miss = None
    author_grams_freq = None
    item = None
    line = None
    yitem = None
    gram_code = None
    gram_count = None
    xxx = None

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

timing2_end = time.time()
timing2_elapsed = round((timing2_end - timing2_start), 8)
print("DONE -1- Save-authors-4grams: '%s' - '%s'" % (timing2_elapsed, human_elapsed(timing2_elapsed),))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# write in ONE file the content of all ".b64usafe" files 


timing3_start = time.time()

all_new_files = absoluteFilePaths(main_directory)

all_agram_files = list()
for xitem in all_new_files:
    if not ("/._" in xitem):
        if xitem.endswith(".a4gramsf"):
            all_agram_files.append(xitem)

if not (len(authors_path) == len(all_agram_files)):
    print("Number authors ", len(authors_path))
    print("Number authors files ", len(all_agram_files))
    raise AssertionError("Number authors not equal number author files")

# get list of authors
b64usafe_paths = list()
for item in authors_path:
    author = item.replace(main_directory, "").split("/")[1]
    b64usafe_paths.append(item + author + ".a4gramsf")

with io.open(temp_file, 'w') as wfg:
    wfg.write("")

with io.open(temp_file, 'a') as wtf:
    for item in b64usafe_paths:
        author = item.replace(main_directory, "").split("/")[1]
        if os.path.isfile(item):
            with io.open(item, 'r') as rif:
                for line in rif:
                    if line:
                        xitem = line.replace("\n", "")
                        gram_code = xitem.split(",")[0].strip()
                        gram_count = int(xitem.split(",")[1].strip())
                        xline = gram_code + "," + author + "\n"
                        wtf.write(xline)

all_new_files = None
all_agram_files = None
xitem = None
b64usafe_paths = None
item = None
author = None
b64usafe_paths = None
line = None
gram_code = None
gram_count = None
xline = None

timing3_end = time.time()
timing3_elapsed = round((timing3_end - timing3_start), 8)
print("DONE -1- Write-temp-file: '%s' - '%s'" % (timing3_elapsed, human_elapsed(timing3_elapsed),))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# COMPUTE 4grams GLOBAL LIST

timing0_start = time.time()

all_authors_frequencies = dict()

# process files PER AUTHOR
for xpath in authors_path:

    author = xpath.replace(main_directory, "").split("/")[1]
    author_freq_file = xpath + author + ".a4gramsf"

    if os.path.isfile(author_freq_file):

        with io.open(author_freq_file, 'r') as rff:
            for line in rff:
                xitem = line.replace("\n", "")
                gram_code = xitem.split(",")[0].strip()
                gram_count = int(xitem.split(",")[1].strip())

                if gram_code in all_authors_frequencies:
                    all_authors_frequencies[gram_code] = all_authors_frequencies[gram_code] + gram_count
                else:
                    all_authors_frequencies[gram_code] = gram_count

sorted_fr = sorted(all_authors_frequencies.items(), key=operator.itemgetter(1), reverse=True)
od_sorted_fr = OrderedDict(sorted_fr)

# write to file aggregated frequencies, across ALL AUTHORS and for ALL files
with io.open(total_frequencies, 'w') as wgf:
    for k, v in od_sorted_fr.items():
        xxx = "%s,%s\n" % (k, v)
        wgf.write(xxx)

all_authors_frequencies = None
author = None
author_freq_file = None
line = None
xitem = None
gram_code = None
gram_count = None
sorted_fr = None
od_sorted_fr = None
xxx = None

timing0_end = time.time()
timing0_elapsed = round((timing0_end - timing0_start), 8)
print("DONE -1- Save-global-4grams-freq: '%s' - '%s'" % (timing0_elapsed, human_elapsed(timing0_elapsed),))

timing8_start = time.time()

temp_dict = OrderedDict()

with io.open(temp_file, 'r') as rtf:
    for line in rtf:
        xline = line.replace("\n", "").strip()
        ngram = xline.split(",")[0].strip()
        author = xline.split(",")[1].strip()

        if not (ngram in temp_dict):
            temp_dict[ngram] = [author]
        else:
            if not author in temp_dict[ngram]:
                temp_dict[ngram].append(author)

dedup_grams_authors = OrderedDict()

for k, v in temp_dict.items():
    # keep only grams seen in AT LEAST 2 AUTHORS
    if (len(v) > 1):
        dedup_grams_authors[k] = len(v)

with io.open(valid_grams, 'w') as rvg:
    for k, v in dedup_grams_authors.items():
        rvg.write(k + "\n")

temp_dict = None
line = None
xline = None
ngram = None
author = None
dedup_grams_authors = None

timing8_end = time.time()
timing8_elapsed = round((timing8_end - timing8_start), 8)
print("DONE -1- Find-duplicates: '%s' - '%s'" % (timing8_elapsed, human_elapsed(timing8_elapsed),))

sys.exit()