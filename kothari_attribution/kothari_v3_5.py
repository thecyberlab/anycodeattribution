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
import base64
import time
from datetime import timedelta
import json
import csv

# ==============================================================================

# Get the directory of the script being executed
script_directory = os.path.dirname(os.path.abspath(__file__))
config_path = script_directory + "/kothari_config.json"

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

result_file = main_directory+separator+kothari_config["result_file"]
basename = main_directory.split("/")[-1]
result_file_csv = main_directory+separator+basename+'_'+kothari_config["result_file_csv"]

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
author_files = OrderedDict()

author_4gramsf = OrderedDict()

for item in all_files:
    if not ("/._" in item):
        if item.endswith(extension):

            java_files.append(item)
            gramf = item[:-len(extension)] + ".4gramsf"

            author = item.replace(main_directory, "").split("/")[1]
            author_path = main_directory + "/" + author + "/"

            authors_path.append(author_path)

            if os.path.isfile(gramf):
                if not author in author_files:
                    author_4gramsf[author] = [gramf]
                else:
                    author_4gramsf[author].append(gramf)
            else:
                print("Java: ", item)
                print("Missing: ", gramf)
                raise AssertionError("ERROR - expected 4gramsf file missing")

            if not author in author_files:
                author_files[author] = [item]
            else:
                author_files[author].append(item)

java_files = set(java_files)

authors_path = set(authors_path)

timing0_end = time.time()
timing0_elapsed = round((timing0_end - timing0_start), 8)

print()
print("Total AUTHORS found: %s" % (len(authors_path),))
print("Total files found: %s" % (len(java_files),))
print()
print("DONE -5- List files: '%s' - '%s'" % (timing0_elapsed, human_elapsed(timing0_elapsed),))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# LOAD ALL GRAM FILES IN RAM

files_data = OrderedDict()

for aut,flist in author_4gramsf.items():
    for item in flist:
        tempdict = OrderedDict()
        with io.open(item, 'r') as rif:
            for line in rif:
                xline = line.replace("/n", "").strip().split(",")
                xgram = xline[0]
                xval = xline[1]
                tempdict[xgram] = xval

        files_data[item] = tempdict

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# CREATE TABLE OF ALL UNIQUE 4GRAMS IN TOP 50 RATIOS

timing0_start = time.time()

author_top50 = OrderedDict()
author_all_grams = list()
with io.open(result_file, 'r') as rrf:
    for line in rrf:
        sline = line.split("|")
        author = sline[-1].strip()
        del(sline[-1])

        templist = list()
        for item in sline:
            xitem = item.split(",")[0]

            author_all_grams.append(xitem)
            templist.append(xitem)

        author_top50[author] = templist

author_all_grams = set(sorted(author_all_grams))

csv_lines = list()

for k,v in author_4gramsf.items():
    # k --> author name
    # v --> list of .4gramsf files (frequency of all 4grams in file)

    authgrams = set(author_top50[k])

    # parse each file
    for item in v:
        basedict = OrderedDict()
        basedict["author"] = k
        filename = item.split("/")[-1][:-len(extension)] + extension
        safename = base64.urlsafe_b64encode(filename.encode("utf-8"))
        basedict["file"] = safename

        for xx in author_all_grams:
            basedict[xx] = 0

            file_data = files_data[item]
            for gram,val in file_data.items():

                if (gram in authgrams):
                    basedict[gram] = val

        csv_lines.append(basedict)


with io.open(result_file_csv, 'w', encoding='utf-8', newline='') as wrf:
    fc = csv.DictWriter(wrf,
                        fieldnames=csv_lines[0].keys(),
                       )
    fc.writeheader()
    fc.writerows(csv_lines)

timing0_end = time.time()
timing0_elapsed = round((timing0_end - timing0_start), 8)
print("DONE -5- Save-top50-filefreq: '%s' - '%s'" % (timing0_elapsed, human_elapsed(timing0_elapsed),))

sys.exit(0)