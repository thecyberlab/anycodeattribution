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
java_files = set(java_files)

authors_path = list(set(authors_path))
authors_path.sort()
authors_path = set(authors_path)

timing0_end = time.time()
timing0_elapsed = round((timing0_end - timing0_start), 8)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 
# COMPUTE 4grams PER EACH FILE


timing0_start = time.time()

letters = ["i", "j", "k", "l"]

for author,file_list in author_files.items():

    file_list = list(set(file_list))
    file_list.sort()

    first_letter = author[0].lower()
    author_path = main_directory + "/" + author + "/"
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    if (first_letter in letters):

        valid_freq_files = list()

        for xfile in file_list:
            gramfile = xfile.replace("\n","")[:-len(extension)] + ".4gramsf"

            if os.path.isfile(gramfile):
                valid_freq_files.append(gramfile)
            else:
                print("JAVA file: ", xfile)
                print("Missing: ", gramfile)
                raise AssertionError("ERROR - expected gramf file missing")

        # get number of valid files per author
        total_files_author = len(valid_freq_files)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

        # read frequencies from file and put into dictionary
        dict_author_tot_stats = dict()

        # get name of the files with author frequencies
        author_tot_stats = author_path + author + ".a4gramsf"

        # open file and read content
        with io.open(author_tot_stats, 'r') as ras:
            for line in ras:
                xline = line.replace("\n","").split(",")
                dict_author_tot_stats[xline[0]] = int(xline[1])

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

        valid_freq_files = set(valid_freq_files)

        temp_dict = OrderedDict()
        for item in valid_freq_files:
            with io.open(item, 'r') as rif:
                for line in rif:
                    # get 4gram
                    fgram = line.replace("\n","").strip().split(",")[0]
                    # get 4gram frequency IN FILE
                    fval = int(line.replace("\n","").strip().split(",")[1])

                    # get 4gram frequency TOTAL
                    f_tot = dict_author_tot_stats[fgram]

                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

                    if (fval > 0):
                        if (f_tot > 0):
                            frac = (Decimal(str(fval)) / Decimal(str(f_tot)))
                        else:
                            print("Line --> ", line.strip())
                            print("gram --> ", fgram)
                            print("gram_count --> ", fval)
                            print("Total --> ", f_tot)
                            raise AssertionError("ERROR - IND-CON --> division by 0, denominator equal to 0")
                    else:
                        print("Line --> ", line.strip())
                        print("gram --> ", fgram)
                        print("gram_count --> ", fval)
                        print("Total --> ", f_tot)
                        raise AssertionError("ERROR - IND-CON --> gram counter equal to 0")

                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

                    # formula individual file consistency --> (F * log10(F))
                    if (frac > 0):
                        if (frac == 1):
                            ind_con = Decimal(str(0))
                        else:
                            ind_con = frac * frac.log10()
                    else:
                        print("Line --> ", line.strip())
                        print("gram --> ", fgram)
                        print("gram_count --> ", fval)
                        print("Total --> ", f_tot)
                        print("F --> ", frac)
                        raise AssertionError("ERROR - IND-CON --> value 'F' less or equal to 0")

                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

                    # add result to dictionary to calculate the sum of all values
                    if (fgram in temp_dict):
                        temp_dict[fgram] = temp_dict[fgram] + ind_con
                    else:
                        temp_dict[fgram] = ind_con

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

        entropy_ind_cons = OrderedDict()
        for k,v in temp_dict.items():
            newval = v * Decimal(str(-1))
            if (newval > 0):
                entropy_ind_cons[k] = round(newval, 8)
            elif (newval == 0):
                entropy_ind_cons[k] = Decimal(str(0))
            else:
                print(author)
                print(k)
                print(v)
                print(newval)
                print("IND-CON --> ", v)
                raise AssertionError("ERROR - IND-CON --> value less then 0")

        sorted_x = sorted(entropy_ind_cons.items(), key=operator.itemgetter(1), reverse=True)
        od_entropy_ind_cons = OrderedDict(sorted_x)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

        b64_author_ind_cons = author_path + author + ".indcon"
        with io.open(b64_author_ind_cons, 'w') as wgf:
            for k,v in od_entropy_ind_cons.items():
                yyy = ("%s,%s\n") % (k, v)
                wgf.write(yyy)

        if not os.path.exists(b64_author_ind_cons):
            print("MISSING FILE: ", b64_author_ind_cons)
            raise AssertionError("ERROR: expected file is has not been written to disk")


        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    first_letter = None
    author_path = None
    valid_freq_files = None
    xfile = None
    gramfile = None
    total_files_author = None
    dict_author_tot_stats = None
    author_tot_stats = None
    line = None
    xline = None
    valid_freq_files = None
    temp_dict = None
    fgram = None
    fval = None
    f_tot = None
    frac = None
    ind_con = None
    entropy_ind_cons = None
    newval = None
    sorted_x = None
    od_entropy_ind_cons = None
    b64_author_ind_cons = None
    yyy = None


timing0_end = time.time()
timing0_elapsed = round((timing0_end - timing0_start), 8)
print("DONE -2i- Save-ind-consistency: '%s' - '%s'" % (timing0_elapsed, human_elapsed(timing0_elapsed),))

sys.exit(0)