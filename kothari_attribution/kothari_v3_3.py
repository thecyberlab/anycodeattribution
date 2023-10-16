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
result_file_pt = main_directory+separator+kothari_config["result_file_?"]
result_file_0 = main_directory+separator+kothari_config["result_file_0"]
result_file_a = main_directory+separator+kothari_config["result_file_a"]
result_file_e = main_directory+separator+kothari_config["result_file_e"]
result_file_i = main_directory+separator+kothari_config["result_file_i"]
result_file_m = main_directory+separator+kothari_config["result_file_m"]
result_file_q = main_directory+separator+kothari_config["result_file_q"]
result_file_u = main_directory+separator+kothari_config["result_file_u"]
result_file_y = main_directory+separator+kothari_config["result_file_y"]
extension = kothari_config["extension"]

with io.open(result_file_pt, 'w') as wfg:
    wfg.write("")
with io.open(result_file_0, 'w') as wfg:
    wfg.write("")
with io.open(result_file_a, 'w') as wfg:
    wfg.write("")
with io.open(result_file_e, 'w') as wfg:
    wfg.write("")
with io.open(result_file_i, 'w') as wfg:
    wfg.write("")
with io.open(result_file_m, 'w') as wfg:
    wfg.write("")
with io.open(result_file_q, 'w') as wfg:
    wfg.write("")
with io.open(result_file_u, 'w') as wfg:
    wfg.write("")
with io.open(result_file_y, 'w') as wfg:
    wfg.write("")

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

author_files = list()
# process total frequency file of AUTHOR
for xpath in authors_path:

    author = xpath.replace(main_directory, "").split("/")[1]
    author_path = main_directory + "/" + author + "/"

    author_freq_file = author_path + author + ".a4gramsf"

    if not author_freq_file in author_files:

        if os.path.isfile(author_freq_file):
            author_files.append(author_freq_file)
        else:
            print("Missing: ", author_freq_file)
            raise AssertionError("ERROR - expected a4gramsf file missing")

author_path = None
del(author_path)
author_freq_file = None
del(author_freq_file)
author = None
del(author)

# load ALL frequencies
all_freq = dict()
with io.open(total_frequencies, 'r') as rtf:
    for line in rtf:
        xkey = line.replace("\n","").split(",")[0]
        xval = int(line.replace("\n","").split(",")[1])
        all_freq[xkey] = xval

# load each author frequency file and calculate population 

for item in author_files:

    temp_dict = OrderedDict()

    author = item.replace(main_directory, "").split("/")[1]
    author_path = main_directory + "/" + author + "/"

    with io.open(item, 'r') as rif:
        for line in rif:
            # get 4gram
            fgram = line.replace("\n","").strip().split(",")[0]
            # get 4gram frequency IN FILE
            fval = int(line.replace("\n","").strip().split(",")[1])
            # get 4gram frequency TOTAL
            f_tot = all_freq[fgram]
            if (f_tot == 0):
                frac = Decimal(str(0))
            else:
                frac = (Decimal(str(fval)) / Decimal(str(f_tot)))
            if (frac == 0):
                ind_con = Decimal(str(0))
            else:
                ind_con = frac * frac.log10()
            # add result to dictionary to calculate the sum of all values
            if (fgram in temp_dict):
                temp_dict[fgram] = temp_dict[fgram] + ind_con
            else:
                temp_dict[fgram] = ind_con

    entropy_pop_cons = OrderedDict()
    for k,v in temp_dict.items():
        newval = -v
        if (newval == 0):
            entropy_pop_cons[k] = Decimal(str(0))
        else:
            entropy_pop_cons[k] = round(newval, 8)

    sorted_x = sorted(entropy_pop_cons.items(), key=operator.itemgetter(1), reverse=True)
    od_entropy_pop_cons = OrderedDict(sorted_x)
    b64_author_pop_cons = author_path + author + ".popcon"

    with io.open(b64_author_pop_cons, 'w') as wgf:
        for k,v in od_entropy_pop_cons.items():
            yyy = ("%s,%s\n") % (k, v)
            wgf.write(yyy)

    if not os.path.exists(b64_author_pop_cons):
        print("MISSING FILE: ", b64_author_pop_cons)
        raise AssertionError("ERROR: expected file is has not been written to disk")

timing0_end = time.time()
timing0_elapsed = round((timing0_end - timing0_start), 8)
print("DONE -3- Save-pop-consistency: '%s' - '%s'" % (timing0_elapsed, human_elapsed(timing0_elapsed),))

sys.exit(0)