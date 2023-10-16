import sys
import io
import os
from collections import OrderedDict
import base64


def absoluteFilePaths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def file_lines(fname):
    # UnicodeDecodeError: 'utf8' codec can't decode byte 0xce in position 601: invalid continuation byte
    with io.open(fname, "r", encoding='utf-8', errors='ignore') as f:
        for i, l in enumerate(f):
            pass
    return i + 1


# ##############################################################################
main_directory = str(sys.argv[-1])

separator = "/"
error_file = main_directory + separator + "caliskan_errors.txt"

all_files = absoluteFilePaths(main_directory)

csv_file = main_directory + separator + main_directory.split(separator)[-1] + "_caliskan_results.csv"

# ##############################################################################


# grab file list

files_java = list()
files_lf = list()
files_nf = list()
files_dl = list()
files_nd = list()
files_bi = list()
files_nug = list()
files_lug = list()
files_max = list()
files_kwd = list()
files_res = list()

# count files by extension
for item in all_files:
    if item.endswith(".java"):
        files_java.append(item)
    if item.endswith(".lf"):
        files_lf.append(item)
    elif item.endswith(".nf"):
        files_nf.append(item)
    elif item.endswith(".dl"):
        files_dl.append(item)
    elif item.endswith(".nd"):
        files_nd.append(item)
    elif item.endswith(".bi"):
        files_bi.append(item)
    elif item.endswith("_term_freq_unigram.arff"):
        files_nug.append(item)
    elif item.endswith("_term_freq_lv.finallf"):
        files_lug.append(item)
    elif item.endswith(".max"):
        files_max.append(item)
    elif item.endswith(".keyword"):
        files_kwd.append(item)
    elif item.endswith(".results"):
        files_res.append(item)

files_lf_ok = list()
files_nf_ok = list()
files_dl_ok = list()
files_nd_ok = list()
files_bi_ok = list()
files_nug_ok = list()
files_lug_ok = list()
files_max_ok = list()
files_kwd_ok = list()
files_res_ok = list()

# check if files we want are in file lists
for item in files_java:

    basename = item.strip().split("/")[-1]
    basepath = item.replace(basename, "")

    xname = basename[0:-5]

    item_lf = basepath + xname + ".lf"
    item_nf = basepath + xname + ".nf"
    item_dl = basepath + xname + ".dl"
    item_nd = basepath + xname + ".nd"
    item_bi = basepath + xname + ".bi"
    item_nug = basepath + xname + "_term_freq_unigram.arff"
    item_lug = basepath + xname + "_term_freq_lv.finallf"
    item_max = basepath + xname + ".max"
    item_kwd = basepath + xname + ".keyword"
    item_res = basepath + xname + ".results"

    if item_lf in files_lf:
        files_lf_ok.append(item_lf)
    if item_nf in files_nf:
        files_nf_ok.append(item_nf)
    if item_dl in files_dl:
        files_dl_ok.append(item_dl)
    if item_nd in files_nd:
        files_nd_ok.append(item_nd)
    if item_bi in files_bi:
        files_bi_ok.append(item_bi)
    if item_nug in files_nug:
        files_nug_ok.append(item_nug)
    if item_lug in files_lug:
        files_lug_ok.append(item_lug)
    if item_max in files_max:
        files_max_ok.append(item_max)
    if item_kwd in files_kwd:
        files_kwd_ok.append(item_kwd)
    if item_res in files_res:
        files_res_ok.append(item_res)

files_java_ok = list()
for item in files_java:

    basename = item.strip().split("/")[-1]
    basepath = item.replace(basename, "")

    xname = basename[0:-5]

    item_lf = basepath + xname + ".lf"
    item_nf = basepath + xname + ".nf"
    item_dl = basepath + xname + ".dl"
    item_nd = basepath + xname + ".nd"
    item_bi = basepath + xname + ".bi"
    item_nug = basepath + xname + "_term_freq_unigram.arff"
    item_lug = basepath + xname + "_term_freq_lv.finallf"
    item_max = basepath + xname + ".max"
    item_kwd = basepath + xname + ".keyword"
    item_res = basepath + xname + ".results"

    if item_lf in files_lf_ok:
        if item_nf in files_nf_ok:
            if item_dl in files_dl_ok:
                if item_nd in files_nd_ok:
                    if item_bi in files_bi_ok:
                        if item_nug in files_nug_ok:
                            if item_lug in files_lug_ok:
                                if item_max in files_max_ok:
                                    if item_kwd in files_kwd_ok:
                                        if item_res in files_res_ok:
                                            files_java_ok.append(item)

files_lf = None
del (files_lf)
files_nf = None
del (files_nf)
files_dl = None
del (files_dl)
files_nd = None
del (files_nd)
files_bi = None
del (files_bi)
files_nug = None
del (files_nug)
files_lug = None
del (files_lug)
files_max = None
del (files_max)
files_kwd = None
del (files_kwd)
files_res = None
del (files_res)
files_java = None
del (files_java)

# CHECK ALL EXTENSIONS HAVE SAME COUNT
xjv = len(files_java_ok)
xlf = len(files_lf_ok)
xnf = len(files_nf_ok)
xdl = len(files_dl_ok)
xnd = len(files_nd_ok)
xbi = len(files_bi_ok)
xnug = len(files_nug_ok)
xlug = len(files_lug_ok)
xmax = len(files_max_ok)
xkwd = len(files_kwd_ok)
xres = len(files_res_ok)

if not (xlf == xnf == xdl == xnd == xbi == xnug == xlug == xmax == xjv == xkwd == xres):
    print("JAVA: ", xjv)
    print("LF: ", xlf)
    print("NF: ", xnf)
    print("DL: ", xdl)
    print("ND: ", xnd)
    print("BI: ", xbi)
    print("NUG: ", xnug)
    print("LUG: ", xlug)
    print("MAX: ", xmax)
    print("KWD: ", xkwd)
    print("RES: ", xres)
    print("ERROR: file mismatch")

# ##############################################################################

filepath_items = OrderedDict()
filepath_feat = OrderedDict()

all_features = list()
print("Start Processing")
FileCount = 0
FeatCount = 0
for item in files_java_ok:
    FileCount = FileCount + 1
    counters = OrderedDict()

    item = item.strip()

    author = item.split("/")[-3]
    group = item.split("/")[-2]

    basename = item.split("/")[-1]
    basepath = item.replace(basename, "")

    xname = basename[0:-5]

    item_lf = basepath + xname + ".lf"
    item_nf = basepath + xname + ".nf"
    item_dl = basepath + xname + ".dl"
    item_nd = basepath + xname + ".nd"
    item_bi = basepath + xname + ".bi"
    item_nug = basepath + xname + "_term_freq_unigram.arff"
    item_lug = basepath + xname + "_term_freq_lv.finallf"
    item_max = basepath + xname + ".max"
    item_kwd = basepath + xname + ".keyword"
    item_res = basepath + xname + ".results"

    # PARSE ND
    with io.open(item_nd, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            elems = xline.split(" = ")
            xk = elems[0]
            xv = elems[1]
            xkenc = base64.urlsafe_b64encode(xk.encode("utf-8"))
            xxkenc = "ND|" + str(xkenc)[2:-1]
            counters[xxkenc] = xv

    # PARSE NF
    with io.open(item_nf, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            elems = xline.split(" = ")
            xk = elems[0]
            xv = elems[1]
            xkenc = base64.urlsafe_b64encode(xk.encode("utf-8"))
            xxkenc = "NF|" + str(xkenc)[2:-1]
            counters[xxkenc] = xv

    # PARSE MAX
    with io.open(item_max, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            elems = xline.split(" = ")
            xk = elems[0]
            xv = elems[1]
            xkenc = base64.urlsafe_b64encode(xk.encode("utf-8"))
            xxkenc = "MAX|" + str(xkenc)[2:-1]
            counters[xxkenc] = xv

    # PARSE RESULTS
    with io.open(item_res, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            if " === " in xline:
                if xline.startswith("F"):
                    xk = xline.split(" === ")[0].split(":")[0]
                    xv = xline.split(" === ")[1]
                    counters[xk] = xv

    # PARSE KEYWORD
    with io.open(item_kwd, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            if " === " in xline:
                if xline.startswith("D"):
                    xk = xline.split(" === ")[0].split(":")[0]
                    xv = xline.split(" === ")[1]
                    counters[xk] = xv

    # PARSE LF
    with io.open(item_lf, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            elems = xline.split("  =====  ")
            if len(elems) == 2:
                xk = elems[0]
                xv = elems[1]

                if len(xk) > 0:
                    xkenc = base64.urlsafe_b64encode(xk.encode("utf-8"))
                    xxkenc = "LF|" + str(xkenc)[2:-1]
                    counters[xxkenc] = xv

    # PARSE DL
    with io.open(item_dl, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            elems = xline.split("  =====  ")
            if len(elems) == 2:
                xk = elems[0]
                xv = elems[1]

                if len(xk) > 0:
                    xkenc = base64.urlsafe_b64encode(xk.encode("utf-8"))
                    xxkenc = "DL|" + str(xkenc)[2:-1]
                    counters[xxkenc] = xv

    # PARSE BI
    with io.open(item_bi, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            elems = xline.split("=")
            if len(elems) == 2:
                xk = elems[0]
                xv = elems[1]
                xkenc = base64.urlsafe_b64encode(xk.encode("utf-8"))
                xxkenc = "BI|" + str(xkenc)[2:-1]
                counters[xxkenc] = xv

    # PARSE NUG
    with io.open(item_nug, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            elems = xline.split(" === ")
            if len(elems) == 2:
                xk = elems[0]
                xv = elems[1]

                if len(xk) > 0:
                    xkenc = base64.urlsafe_b64encode(xk.encode("utf-8"))
                    xxkenc = "NUG|" + str(xkenc)[2:-1]
                    counters[xxkenc] = xv

    # PARSE LUG
    with io.open(item_lug, 'r', encoding='utf-8', errors='ignore') as rfl:
        for line in rfl:
            xline = line.strip()
            elems = xline.split(" === ")
            if len(elems) == 2:
                xk = elems[0]
                xv = elems[1]

                if len(xk) > 0:
                    xkenc = base64.urlsafe_b64encode(xk.encode("utf-8"))
                    xxkenc = "LUG|" + str(xkenc)[2:-1]
                    counters[xxkenc] = xv

    filepath_items[item] = [basename, author, group]

    filepath_feat[item] = counters

    for k, v in counters.items():
        if not k in all_features:
            all_features.append(k)

    FeatCount = FeatCount + len(counters)
    print(str(FileCount), " Features Num:", str(FeatCount))

all_features = sorted(all_features)

# ##############################################################################


header_csv = ["FilePath", "Basename", "Author", "Lines-Group"]
for item in all_features:
    header_csv.append(item)

with io.open(csv_file, 'w') as wsv:
    xstr = ",".join(header_csv) + "\n"
    wsv.write(xstr)

    for k, v in filepath_items.items():

        result = list()

        result.append(k)
        result.append(v[0])
        result.append(v[1])
        result.append(v[2])

        for item in all_features:
            if item in filepath_feat[k]:
                temp = str(filepath_feat[k][item])
            else:
                temp = str(0)
            result.append(temp)

        # CHECK RESULT LENGTH
        if not len(result) == len(header_csv):
            print("header: ", len(header_csv))
            print("results: ", len(result))
            print("ERROR: line and header not same length")

        rstr = ",".join(result) + "\n"
        wsv.write(rstr)

sys.exit(0)
