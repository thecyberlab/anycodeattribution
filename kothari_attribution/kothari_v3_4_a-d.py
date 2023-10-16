#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This code allows to extract Kothari et al. features (described in Kothari et al. study https://ieeexplore.ieee.org/document/4151691) from source code files. 
#The main output file is kothari.arff, which contains Kothari et al. feature vectors.

#This code should be located in the same folder as input files and can be executed by any Python IDEs.

import io
import sys
import os
import os.path
from collections import OrderedDict
import operator
import time
from datetime import timedelta
from decimal import Decimal
import json

# ==============================================================================

def absoluteFilePaths(directory):
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))

def string_chunks(input_string, chunk_size):
    chunk_size = int(chunk_size)
    result = [input_string[i:i+chunk_size] for i in range(0, len(input_string), chunk_size)]
    return(result)

def slidingWindow(sequence,winSize,step=1):
    """Returns a generator that will iterate through
    the defined chunks of input sequence.  Input sequence
    must be iterable."""
 
    temp = list()
    # Verify the inputs
    try: it = iter(sequence)
    except TypeError:
        raise Exception("**ERROR** sequence must be iterable.")
    if not ((type(winSize) == type(0)) and (type(step) == type(0))):
        raise Exception("**ERROR** type(winSize) and type(step) must be int.")
    if step > winSize:
        raise Exception("**ERROR** step must not be larger than winSize.")
    if winSize > len(sequence):
        raise Exception("**ERROR** winSize must not be larger than sequence length.")
 
    # Pre-compute number of chunks to emit
    numOfChunks = int(((len(sequence)-winSize)/step)+1)

    # Do the work
    for i in range(0,numOfChunks*step,step):
        temp.append(sequence[i:i+winSize])
    return(temp)

# ==============================================================================

# Get the directory of the script being executed
script_directory = os.path.dirname(os.path.abspath(__file__))
config_path = script_directory + "/kothari_config.json"

# Read JSON file
with io.open(config_path, 'r') as rcf:
    kothari_config = json.load(rcf)


# TEST with 1 folder
main_directory = str(sys.argv[-1])
separator = kothari_config["separator"]
error_file = script_directory + "/kothari_errors.txt"
valid_grams = main_directory+separator+kothari_config["valid_grams"]
temp_file = main_directory+separator+kothari_config["temp_file"]
total_frequencies = main_directory+separator+kothari_config["total_frequencies"]
result_file_0 = main_directory+separator+kothari_config["result_file_0"]
result_file_a = main_directory+separator+kothari_config["result_file_a"]
result_file_e = main_directory+separator+kothari_config["result_file_e"]
result_file_i = main_directory+separator+kothari_config["result_file_i"]
result_file_m = main_directory+separator+kothari_config["result_file_m"]
result_file_q = main_directory+separator+kothari_config["result_file_q"]
result_file_u = main_directory+separator+kothari_config["result_file_u"]
result_file_y = main_directory+separator+kothari_config["result_file_y"]
extension = kothari_config["extension"]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def human_elapsed(epoch_time):
    res = str(timedelta(seconds=epoch_time))
    return(res)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 
# GET FILE LIST

timing0_start = time.time()

all_files = absoluteFilePaths(main_directory)

# list JAVA files
java_files = list()

# list AUTHORS
authors_path = list()
author_files = dict()


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


java_files = list(set(java_files))
java_files.sort()

authors_path = list(set(authors_path))
authors_path.sort()

timing0_end = time.time()
timing0_elapsed = round((timing0_end - timing0_start), 8)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 
# COMPUTE 4grams PER EACH FILE


timing0_start = time.time()

author_files_ind = list()
author_files_pop = list()
# process total frequency file of AUTHOR
for xpath in authors_path:
    author = xpath.replace(main_directory, "").split("/")[1]
    author_path = main_directory + "/" + author + "/"

    author_file_ind = author_path + author + ".indcon"
    if not author_file_ind in author_files_ind:
        if os.path.isfile(author_file_ind):
            author_files_ind.append(author_file_ind)
        else:
            print("Missing: ", author_file_ind)
            raise AssertionError("ERROR - expected indcon file missing")

    author_file_pop = author_path + author + ".popcon"
    if not author_file_pop in author_files_pop:
        if os.path.isfile(author_file_pop):
            author_files_pop.append(author_file_pop)
        else:
            print("Missing: ", author_file_pop)
            raise AssertionError("ERROR - expected popcon file missing")

author_path = None
del(author_path)
author = None
del(author)
author_file_ind = None
del(author_file_ind)
author_file_pop = None
del(author_file_pop)

# load ALL frequencies
all_freq = dict()
with io.open(total_frequencies, 'r') as rtf:
    for line in rtf:
        xkey = line.replace("\n","").split(",")[0]
        xval = int(line.replace("\n","").split(",")[1])
        all_freq[xkey] = xval

# load ALL VALID frequencies (4gram seen in AT LEAST 2 authors)
valid_freq = list()
with io.open(valid_grams, 'r') as rvf:
    for line in rvf:
        zkey = line.replace("\n","")
        valid_freq.append(zkey)
valid_freq = set(valid_freq)

letters = ["a", "b", "c", "d"]

for item in author_files_ind:

    author = item.replace(main_directory, "").split("/")[1]
    author_path = main_directory + "/" + author + "/"

    first_letter = author[0].lower()

    if (first_letter in letters):

        author_ratios = OrderedDict()
        author_file_pop = author_path + author + ".popcon"

        # load individual consistency
        load_int_con = dict()
        with io.open(item, 'r') as ric:
            for line in ric:
                ikey = line.replace("\n","").strip().split(",")[0]
                ival = line.replace("\n","").strip().split(",")[1]
                load_int_con[ikey] = ival

        # load population consistency
        load_pop_con = dict()
        with io.open(author_file_pop, 'r') as rpc:
            for line in rpc:
                pkey = line.replace("\n","").strip().split(",")[0]
                pval = line.replace("\n","").strip().split(",")[1]
                load_pop_con[pkey] = pval

        # compute all ratios
        # S --> (individual consistency / population consistency)
        for k,v in load_int_con.items():

            ind_con = Decimal(str(v))
            pop_con = Decimal(str(load_pop_con[k]))
            if pop_con > 0:
                if ind_con > 0:
                    xratio = round((ind_con / pop_con), 8)

                    # add result to dictionary to calculate the sum of all values
                    author_ratios[k] = xratio

        sorted_x = sorted(author_ratios.items(), key=operator.itemgetter(1), reverse=True)
        od_author_ratios = OrderedDict(sorted_x)

        b64_author_ratios = author_path + author + ".ratios"
        with io.open(b64_author_ratios, 'w') as wgf:
            for k,v in od_author_ratios.items():
                yyy = ("%s,%s\n") % (k, v)
                wgf.write(yyy)

        if not os.path.exists(b64_author_ratios):
            print("MISSING FILE: ", b64_author_ratios)
            raise AssertionError("ERROR: expected file is has not been written to disk")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

        valid_grams = OrderedDict()

        for k,v in od_author_ratios.items():
            if (k in valid_freq):
                
                valid_grams[k] = v

        b64_author_ratios = author_path + author + ".vratios"
        with io.open(b64_author_ratios, 'w') as wvf:
            for k,v in valid_grams.items():
                yyy = ("%s,%s\n") % (k, v)
                wvf.write(yyy)

        if not os.path.exists(b64_author_ratios):
            print("MISSING FILE: ", b64_author_ratios)
            raise AssertionError("ERROR: expected file is has not been written to disk")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

        if (len(valid_grams) > 49):
            top_50 = list(valid_grams.items())[:50]
        else:
            top_50 = list(valid_grams.items())
        # [(0, 'a'), (1, 'b'), (2, 'c')]

        b64_author_top50 = author_path + author + ".topvratios"
        with io.open(b64_author_top50, 'w') as wtf:
            for item in top_50:
                yyy = ("%s,%s\n") % (item[0], item[1])
                wtf.write(yyy)

        if not os.path.exists(b64_author_top50):
            print("MISSING FILE: ", b64_author_top50)
            raise AssertionError("ERROR: expected file is has not been written to disk")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

        list_arff = list()
        for item in top_50:
            tval = "%s,%s" % (item[0], item[1])
            list_arff.append(str(tval))
        list_arff.append(author)
        result = '|'.join(list_arff)

        with io.open(result_file_a, 'a') as wrf:
            wrf.write(result + "\n")

timing0_end = time.time()
timing0_elapsed = round((timing0_end - timing0_start), 8)
print("DONE -4a- Save-top50-ratios: '%s' - '%s'" % (timing0_elapsed, human_elapsed(timing0_elapsed),))

sys.exit(0)