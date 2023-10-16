import os
import io
import sys
import csv
from collections import OrderedDict
import pathlib

input_Dataset = str(sys.argv[-1])

sally_out = input_Dataset+'_res_sw_xf_all_t50.txt'

sally_parsed = input_Dataset + ".csv"
sally_parsed_top50 = input_Dataset + "-top50.csv"
Code_gram = input_Dataset + "_cg.csv"

parsed_results = list()
author_codes_vals = OrderedDict()
code_gram = dict()

# check if DIR is there
if not os.path.isdir(input_Dataset):
    raise AssertionError("ERROR: input folder NOT found")

all_files = list()

for path, subdirs, files in os.walk(input_Dataset):
    for name in files:
        all_files.append(pathlib.PurePath(path, name))

for item in all_files:
    
    ext = str(item).split(".")[1].strip().lower()
    if ext == "png":
        os.remove(item)
    elif ext == "txt":
        os.remove(item)

# ============================================================================

line_number = 0
nonparsed = 0

listdict = OrderedDict()

with io.open(sally_out, 'r') as rif:
    for line in rif:
        line_number = line_number + 1

        xline = line.strip().replace("\n", "")
        cells = xline.split(",")

        listdict[cells[-1].split('#')[1]]= len(cells)

        filepath = ""
        author = ""
        group = ""
        filename = ""

        code_value = dict()

        for item in cells:
            xitem = item.strip()

            if xitem:
                if ":" in xitem:

                    if " # " in xitem:
                        fitem = xitem.split(" # ")[1].strip()
                        filepath = fitem

                        author = fitem.split("/")[-3]
                        group = fitem.split("/")[-2]
                        filename = fitem.split("/")[-1]
                        xxitem = xitem.split(" # ")[0].strip().split(":")

                    else:
                        xxitem = xitem.split(":")

                    xcode = str(xxitem[0])

                    xval = xxitem[2]

                    code_value[xcode] = xval
                    code_gram[xcode] = xxitem[1]

                    if author in author_codes_vals:
                        if xcode in author_codes_vals[author]:
                            author_codes_vals[author][xcode] = author_codes_vals[author][xcode] + xval
                        else:
                            author_codes_vals[author][xcode] = xval
                    else:
                        author_codes_vals[author] = OrderedDict()
                        author_codes_vals[author][xcode] = xval

        sorted_x = sorted(code_value.items(), key=lambda kv: kv[1], reverse=True)
        sorted_dict = OrderedDict(sorted_x)

        if (filepath or author or group or filename) == "":
            nonparsed = nonparsed +1
            print("Line -> ", xline)
            print("Line-number -> ", line_number)
            print("File Cannot be parsed")

        line_parsed = list()
        file_result = [filepath, author, group, filename]
        for xx in file_result:
            line_parsed.append(xx)

        for k, v in sorted_dict.items():
            xcd = str(k) + "," + str(v)
            line_parsed.append(xcd)

        # DONE, line parsed, adding to main list
        parsed_results.append(line_parsed)

# ============================================================================
for item in listdict:
    print(item,listdict[item])

with io.open(sally_parsed, 'w') as wpf:
    for item in parsed_results:

        try:
            xitem = ",".join(item) + "\n"
        except Exception as e:
            print(item)
            print(e)
            raise

        wpf.write(xitem)

# ============================================================================

all_top50_codes = list()
for ax, cx in author_codes_vals.items():
    # get author, list codes:vals
    sorted_code_vals = sorted(cx.items(), key=lambda kv: kv[1], reverse=True)
    sorted_author_codes_vals = OrderedDict(sorted_code_vals)
    if len(sorted_author_codes_vals.keys()) >= 50:
        top_50_codes = list(sorted_author_codes_vals.keys())[0:50]
    else:
        top_50_codes = list(sorted_author_codes_vals.keys())

    for item in top_50_codes:
        all_top50_codes.append(item)

all_top50_codes = list(set(all_top50_codes))

print("Total number of files that were not parsed : " + str(nonparsed) )
print("Total number of features :" + str(len(all_top50_codes)))

# ============================================================================

final_top50_code_vals = list()
for yy in parsed_results:

    code_vals = dict()

    filepath = yy[0]
    author = yy[1]
    group = yy[2]
    filename = yy[3]
    xxitems = yy[4:]
    for item in xxitems:
        xycv = item.split(",")
        ycode = xycv[0]
        yval = xycv[1]
        code_vals[ycode] = yval

    sorted_top50 = list()
    for code in all_top50_codes:
        if code in code_vals:
            sorted_top50.append(str(code_vals[code]))
        else:
            sorted_top50.append(str(0))

    final_top50_line = [filepath, author, group, filename]
    for item in sorted_top50:
        final_top50_line.append(item)

    final_top50_code_vals.append(final_top50_line)

# ============================================================================

final_csv = list()
csv_header = ["fullpath", "Author", "Group", "Filename"]
for item in all_top50_codes:
    csv_header.append(item)

if not len(csv_header) == (len(all_top50_codes) + 4):
    print(csv_header)
    print("Len-codes -> ", len(all_top50_codes))
    raise AssertionError("ERROR: csv header has invalid length")
final_csv.append(csv_header)

for xline in final_top50_code_vals:
    if not len(xline) == (len(all_top50_codes) + 4):
        print(xline)
        print("Len-codes -> ", len(all_top50_codes))
        print("Len-line -> ", len(xline))
        raise AssertionError("ERROR: line with invalid length")
    final_csv.append(xline)

print("Total number of files :" + str(len(final_csv)-1-nonparsed))

with io.open(sally_parsed_top50, 'w') as wfc:
    for item in final_csv:
        xitem = ",".join(item) + "\n"
        wfc.write(xitem)

# ============================================================================

w = csv.writer(open(Code_gram, "w"))
for key, val in code_gram.items():
    if key in all_top50_codes:
        w.writerow([key,val])

# ===========================================================================

sys.exit()