# This code allows to extract Caliskan et al. features (described in Caliskan et al. study
# https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-caliskan-islam.pdf)
# from java source code files using earlier parsed files from step 2.1 in https://github.com/alinamatyukhina/Attribution_Real_World


import sys
import math
from collections import Counter
from collections import OrderedDict

import os
import io

separator = "/"

# ========================= FUNCTIONS ========================================= #

"""
Divided a string into n-grams
s: a string
n: the size of the gram; default is 2
i: the index at which we begin breaking the string into n-grams; default is 0
"""


def ngrams(s, n=2, i=0):
    while len(s[i:i + n]) == n:
        yield s[i:i + n]
        i += 1


"""
For each key-value pair in dictionary, divides the value by the total sum of all the values
my_dict: a dictionary
Return: the given dictionary where the values are divided by the sum of all the values
"""


def div_d(my_dict):
    sum_p = sum(my_dict.values())
    for i in my_dict:
        my_dict[i] = round(float(my_dict[i] / sum_p), 5)
    return my_dict


"""
Given a directory location, obtains all the files in the directory
directory: the starting directory
Yield: the absolute paths of the files in the provided directory
"""


def absoluteFilePaths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


"""
Count the lines in a file
fname: the name of the file
Return: the number of lines in the file
"""


def file_lines(fname):
    count = 0
    # UnicodeDecodeError: 'utf8' codec can't decode byte 0xce in position 601: invalid continuation byte
    if os.path.isfile(fname):
        with io.open(fname, "r", encoding='utf-8', errors='ignore') as f:
            for line in f:
                count = count + 1
    else:
        print("filepath --> ", fname)
        raise AssertionError("ERROR: file NOT found")
    return count


"""
Counts a searched-for character in a list of lines
keychar: the character being searched for
list_of_lines: list containing lines (that are strings?)
"""


def ccount(keychar, list_of_lines):
    count = 0
    for line in list_of_lines:
        for xchar in line:
            if (xchar == keychar):
                count = count + 1
    return (count)


"""
Calculates standard deviation
data: a list containing values
"""


def sd_calc(data):
    n = len(data)

    if n <= 1:
        return 0.0

    mean, sd = avg_calc(data), 0.0

    # calculate std. dev.
    for el in data:
        sd += (float(el) - mean) ** 2
    sd = math.sqrt(sd / float(n - 1))

    return sd


"""
Calculates the average of a list of values
ls: list of values
"""


def avg_calc(ls):
    n, mean = len(ls), 0.0

    # NR adjustment b/c of this error:
    # IndexError: list index out of range
    if n == 0:
        return 0.0

    elif n == 1:
        return ls[0]

    # calculate average
    for el in ls:
        mean = mean + float(el)
    mean = mean / float(n)

    return mean


# ================================================================== #

# NR: Modified file so that code runs from the command line (June 30)
main_directory = str(sys.argv[-1])

error_file = main_directory + separator + "caliskan_errors.txt"

all_files = absoluteFilePaths(main_directory)

# Get list of java files in the dataset folder
java_files = list()
for item in all_files:
    if not ("/._" in item):
        if item.endswith(".java"):
            if not (item in java_files):
                java_files.append(item)
java_files.sort()

# Obtain list of author paths
author_pathnames = list()
for file in java_files:
    author_path = separator.join(file.split(separator)[:-2])
    if author_path not in author_pathnames:
        author_pathnames.append(author_path)
author_pathnames.sort()

# Each author file path key has a list of all its java files
authors_dict = dict()
for author in author_pathnames:
    authors_dict[author] = list()

# Get a list of java files per author
for file in java_files:
    author_folder = separator.join(file.split(separator)[:-2])
    authors_dict[author_folder].append(file)


# ==============================================================================

# FUNCTIONS PER AUTHOR

def all_unigrams_author(tf_unigrams_in, author_unigrams, xauthor, xseparator, xauthor_name):
    all_unigrams_dict = {key: float(0) for key in tf_unigrams_in}

    # Sum the frequency across files in author folder
    for dictionary in author_unigrams:
        for key in dictionary:
            all_unigrams_dict[key] = all_unigrams_dict[key] + dictionary[key]

    # Generate an .arff file of unigram term frequencies for each author
    author_unigram_str = str()
    for key in all_unigrams_dict:
        author_unigram_str = author_unigram_str + key + " === " + str(all_unigrams_dict[key]) + "\n"

    # For each author, write the author term frequencies to an arff file
    results_filename = xauthor + xseparator + xauthor_name + "_term_freq_unigram.arff"

    with io.open(results_filename, 'w') as waf:
        waf.write(author_unigram_str)

    return (all_unigrams_dict)


def author_lv(all_lv_list, xall_tf_lv, xauthor, xseparator, xauthor_name):
    # LF
    # Sum up term frequencies across authors
    author_tf_lv = {key: float(0) for key in all_lv_list}
    for dictionary in xall_tf_lv:
        for key in dictionary:
            author_tf_lv[key] = author_tf_lv[key] + dictionary[key]

    # Generate an .arff file of leaf term frequencies for each author
    lf_lv_str = str()
    for key in author_tf_lv:
        lf_lv_str = lf_lv_str + key + " === " + str(author_tf_lv[key]) + "\n"

    # For each author, write the author term frequencies to an arff file
    results_filename = xauthor + xseparator + xauthor_name + "_term_freq_leaves.arff"

    with io.open(results_filename, 'w') as waf:
        waf.write(lf_lv_str)

    return (author_tf_lv)


def author_nd(all_nd_in, xauthor, xseparator, xauthor_name):
    # Sum term frequency across authors
    author_tf_nd = {key: float(0) for key in all_nd_in}
    for dictionary in author_tf_nd:
        for key in dictionary:
            author_tf_nd[key] = author_tf_nd[key] + dictionary[key]

    # Generate an .arff file of leaf term frequencies for each author
    lf_nd_str = str()
    for key in author_tf_nd:
        lf_nd_str = lf_nd_str + key + " === " + str(author_tf_nd[key]) + "\n"

    # For each author, write the author term frequencies to an arff file
    results_filename = xauthor + xseparator + xauthor_name + "_term_freq_node.arff"

    with io.open(results_filename, 'w') as waf:
        waf.write(lf_nd_str)

    return (author_tf_nd)


def author_dl(all_lv, xauthor_depth_lv, xall_depth_lv, xauthor, xseparator, xauthor_name):
    author_avg_depth = {key: float(0) for key in xall_depth_lv}

    for dictionary in xauthor_depth_lv:
        for key in dictionary:
            author_avg_depth[key] = author_avg_depth[key] + dictionary[key]

    # Generate an .arff file of leaf term frequencies for each author
    depth_lv_str = str()
    for key in author_avg_depth:
        depth_lv_str = depth_lv_str + key + " === " + str(author_avg_depth[key]) + "\n"

    # For each author, write the author term frequencies to an arff file
    results_filename = xauthor + xseparator + xauthor_name + "_av_depth_lv.arff"

    with io.open(results_filename, 'w') as waf:
        waf.write(depth_lv_str)

    return (author_avg_depth)


def author_nd(all_nd_in, all_avg_depth_nd_in, xauthor, xseparator, xauthor_name):
    author_avg_nd_depth = {key: float(0) for key in all_nd_in}

    for dictionary in all_avg_depth_nd_in:
        for key in dictionary:
            author_avg_nd_depth[key] = author_avg_nd_depth[key] + dictionary[key]

    # Generate an .arff file of leaf term frequencies for each author
    depth_nd_str = str()
    for key in author_avg_nd_depth:
        depth_nd_str = depth_nd_str + key + " === " + str(author_avg_nd_depth[key]) + "\n"

    # For each author, write the author term frequencies to an arff file
    results_filename = xauthor + xseparator + xauthor_name + "_av_node_depth.arff"

    with io.open(results_filename, 'w') as waf:
        waf.write(depth_nd_str)

    return (author_avg_nd_depth)


def author_bi(all_bi_in, all_author_bigrams_in, xauthor, xseparator, xauthor_name):
    all_bi_dict = {d: float(0) for d in all_bi_in}

    for dictionary in all_author_bigrams_in:
        for key in dictionary:
            all_bi_dict[key] = all_bi_dict[key] + dictionary[key]

    # Generate an .arff file of bigram term frequencies for each author
    bi_str = str()
    for key in all_bi_dict:
        bi_str = bi_str + key + " === " + str(all_bi_dict[key]) + "\n"

    # For each author, write the author term frequencies to an arff file
    results_filename = xauthor + xseparator + xauthor_name + "_AST.arff"

    with io.open(results_filename, 'w') as waf:
        waf.write(bi_str)

    return (all_bi_dict)


# ==============================================================================


def file_process_1(dictionary_authors):
    # --------------------- TERM FREQUENCY LEAVES ---------------------------- #

    # Masterlist of all leaves used by authors in the dataset
    xall_dataset_lv = list()

    # Stores the individual author dict where the keys are only the leaves used by that author
    xindiv_authors = list()

    # --------------------- TERM FREQUENCY NODES ------------------------------------ #
    all_nd = list()
    temp_res = OrderedDict()

    for author in dictionary_authors:

        tf_unigrams = list()
        all_author_unig = list()

        # LF
        all_tf_lv = list()
        all_lv = list()

        # NF
        all_tf_nd = list()

        # DL
        author_depth_lv = list()

        # ND
        all_avg_depth_nd = list()

        # BI
        all_author_bigrams = list()

        for java_file in dictionary_authors[author]:

            # LF
            all_lines_lf = list()

            # NF
            all_lines_nf = list()

            # ==============================================================================
            # ==============================================================================
            # PER AUTHOR, PER FILE
            # ==============================================================================
            # ==============================================================================

            # READ JAVA FILE
            # FROM JAVA FILE, get all lines with LATIN-1 encoding
            all_lines_latin1 = list()
            if os.path.isfile(java_file):
                with io.open(java_file, 'r', encoding='utf-8', errors='ignore') as rfl:
                    for line in rfl:
                        all_lines_latin1.append(line)
            else:
                print("filepath --> ", java_file)
                raise AssertionError("ERROR: file NOT found")
            if len(all_lines_latin1) == 0:
                print("filepath --> ", java_file)
                print("lines --> ", len(all_lines_latin1))
                raise AssertionError("ERROR: file is EMPTY")

            line_num = file_lines(java_file)

            content = ''.join(all_lines_latin1)
            char_num = len(content)

            # ------------------------------------------------------------------------ #
            bad_file_lf = False
            # READ LF FILE
            # Check for existence of lf file
            lf_file = str(java_file)[:-5] + ".lf"
            if not os.path.isfile(lf_file):
                bad_file_lf = True

                with io.open(error_file, 'a') as waf:
                    waf.write("**** ERROR " + str(java_file) + " \n")
                    waf.write("Missing " + lf_file + " \n")

            # FROM LF FILE, get all lines
            with io.open(lf_file, 'r', encoding='utf-8', errors='ignore') as rfl:
                for line in rfl:
                    all_lines_lf.append(line)

            # ------------------------------------------------------------------------ #
            bad_file_nf = False

            # Check for existence of nf file; ignore corresponding Java file if nf is missing
            nf_file = str(java_file)[:-5] + ".nf"
            if not os.path.isfile(nf_file):
                bad_file_nf = True
                with io.open(error_file, 'a') as waf:
                    waf.write("**** ERROR " + str(java_file) + " \n")
                    waf.write("Missing " + nf_file + " \n")

            # FROM NF FILE, get all lines
            with io.open(nf_file, 'r', encoding='utf-8', errors='ignore') as rfl:
                for line in rfl:
                    all_lines_nf.append(line)

            # ------------------------------------------------------------------------ #
            bad_file_dl = False

            # Ignore corresponding Java file if max file is missing
            dl_file = str(java_file)[:-5] + ".dl"
            if not os.path.isfile(dl_file):
                bad_file_dl = True
                with io.open(error_file, 'a') as waf:
                    waf.write("**** ERROR " + str(java_file) + " \n")
                    waf.write("Missing " + dl_file + " \n")

            # FROM DL FILE, get all lines
            all_lines_dl = list()
            with io.open(dl_file, 'r', encoding='utf-8', errors='ignore') as rfl:
                for line in rfl:
                    all_lines_dl.append(line)

            # ------------------------------------------------------------------------ #

            bad_file_nd = False

            # Check for existence of nd file
            nd_file = str(java_file)[:-5] + ".nd"
            if not os.path.isfile(nd_file):
                bad_file_nd = True
                with io.open(error_file, 'a') as waf:
                    waf.write("**** ERROR " + str(java_file) + " \n")
                    waf.write("Missing " + nd_file + " \n")

            # FROM ND FILE, get all lines
            all_lines_nd = list()
            with io.open(nd_file, 'r', encoding='utf-8', errors='ignore') as rfl:
                for line in rfl:
                    all_lines_nd.append(line)

            # ------------------------------------------------------------------------ #

            bad_file_bi = False

            # Check for existence of bi file
            bi_file = str(java_file)[:-5] + ".bi"
            if not os.path.isfile(bi_file):
                bad_file_bi = True
                with io.open(error_file, 'a') as waf:
                    waf.write("**** ERROR " + str(java_file) + " \n")
                    waf.write("Missing " + bi_file + " \n")


            # FROM BI FILE, get all lines
            all_lines_bi = list()
            with io.open(bi_file, 'r', encoding='utf-8', errors='ignore') as rfl:
                for line in rfl:
                    all_lines_bi.append(line)

            # ===============================================================================

            # For each java file, generate an arff file of unig tf ----------------------- #

            # break code into unigrams
            a = list()
            for line in all_lines_latin1:
                unigram = ngrams(line.split(), n=1)
                unigram_list = list(unigram)
                a.append(unigram_list)

            flattened = [val for sublist in a for val in sublist]
            flattened2 = [val for sublist in flattened for val in sublist]

            # Count how many times unigram appears
            unigram_dict = dict(Counter(flattened2))

            # Calculate the frequency of each unigram's occurence in the code
            freq_dict = div_d(unigram_dict)

            # Keep a master list of all unigrams in author folder
            for key in freq_dict:
                tf_unigrams.append(key)

            all_author_unig.append(freq_dict)

            # Generate an .arff file of unigram term frequencies for each java file
            unigram_str = str()
            for key in freq_dict:
                unigram_str = unigram_str + key + " === " + str(freq_dict[key]) + "\n"

            # For each java file, write the indiv. term frequencies to an arff file
            relative_path = java_file.replace(main_directory, "")
            java_file_name = relative_path.split(separator)[-1]
            path = separator.join(java_file.split(separator)[:-1])
            results_filename = path + separator + java_file_name[:-5] + "_term_freq_unigram.arff"

            with io.open(results_filename, 'w') as waf:
                waf.write(unigram_str)

            # ==============================================================================

            # ------------------------------ LAYOUT FEATURES --------------------------------------- #

            # ------------------------- F3: ln(# empty lines/length) -------------------------------- #

            non_blank_count = 0

            for line in all_lines_latin1:
                if line.strip():
                    non_blank_count += 1

            blank_lines = line_num - non_blank_count

            result = math.log((blank_lines + 1) / char_num)
            result = round(result, 5)

            str_f3 = str(result)

            # author - java_file - "F3: ln(# of empty lines/length)" - VALUE
            xkey = "F3"
            if not author in temp_res:
                temp_res[author] = dict()

            if not java_file in temp_res[author]:
                temp_res[author][java_file] = dict()

            if not xkey in temp_res[author][java_file]:
                temp_res[author][java_file][xkey] = str_f3

            # ------------------------------ LF FEATURES --------------------------------------- #

            if not bad_file_lf:
                # Built all_lines_lf which contains the lines from the *.lf files

                lf_list = [line.split('  =====  ') for line in all_lines_lf]

                # Turn list into a dict where the value is stripped of trailing \n and converted to a float
                # Error in sample_2/aalmiray/101-200/game.java b/c there's a line missing a number
                # We ignore it by only looking at the sublists with 2 items
                freq_leaves_dict = {d[0]: float(d[1][:-1]) for d in lf_list if len(d) == 2}

                # Data in dict would orig be written to *.finallf files
                tf_leaves_dict = div_d(freq_leaves_dict)

                # Generate an .arff file of term frequencies for each java file
                tf_lv_str = str()
                for key in tf_leaves_dict:
                    tf_lv_str = tf_lv_str + key + " === " + str(tf_leaves_dict[key]) + "\n"
                    # Keep a master list of all leaves across the files
                    all_lv.append(key)

                # For each java file, write the indiv. term frequencies to a file
                relative_path = java_file.replace(main_directory, "")
                java_file_name = relative_path.split(separator)[-1]
                path = separator.join(java_file.split(separator)[:-1])
                results_filename = path + separator + java_file_name[:-5] + "_term_freq_lv.finallf"

                with io.open(results_filename, 'w') as waf:
                    waf.write(tf_lv_str)

                all_tf_lv.append(tf_leaves_dict)

            # ------------------------------ NF FEATURES --------------------------------------- #

            if not bad_file_nf:
                nf_list = [line.split(' =') for line in all_lines_nf]

                # Turn list into a dict where the value is stripped of trailing \n and converted to a float
                tf_node = {d[0]: float(d[1][:-1]) for d in nf_list}

                all_tf_nd.append(tf_node)

            # ------------------------------ DL FEATURES --------------------------------------- #

            if not bad_file_dl:
                dl_list = [line.split('  =====  ') for line in all_lines_dl]

                # Turn list into a dict where the value is stripped of trailing \n and converted to a float
                lv_depth_dict = {d[0]: float(d[1][:-1]) for d in dl_list if len(d) == 2}

                author_depth_lv.append(lv_depth_dict)

            # ------------------------------ ND FEATURES --------------------------------------- #

            if not bad_file_nd:

                nd_list = [line.split('=') for line in all_lines_nd]

                # Turn list into a dict where the value is stripped of trailing \n and converted to a float
                avg_nd_depth = {d[0].rstrip(): float(d[1][:-1]) for d in nd_list if len(d) == 2}

                all_avg_depth_nd.append(avg_nd_depth)

                # Build masterlist of all nodes across authors
                for key in all_avg_depth_nd[0]:
                    if key not in all_nd:
                        all_nd.append(key)

            # ------------------------------ BI FEATURES --------------------------------------- #

            if not bad_file_bi:
                bi_list = [line.split('=') for line in all_lines_bi]
                bi_dict = {d[0]: float(d[1][:-1]) for d in bi_list}

                all_author_bigrams.append(bi_dict)

    xres = [temp_res,
            xindiv_authors,
            xall_dataset_lv,
            ]

    return (xres)


# ==============================================================================


file_features = OrderedDict()

results = file_process_1(authors_dict)

res_1 = results[0]
indiv_authors = results[1]
all_dataset_lv = results[2]

# RES_1 --> author - java_file - "F3" - VALUE
for k, v in res_1.items():
    file_features[k] = v

res_1 = None
del (res_1)