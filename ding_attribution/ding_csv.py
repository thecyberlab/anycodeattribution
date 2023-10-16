# Formats the information from results.arff into a csv file 

import io
import sys
import csv

from collections import OrderedDict


# ----------------------------------------------------------

def load_arff(filepath):

    temp = list()

    with io.open(filepath, 'r') as rif:
        for line in rif:
            xline = line.replace("\n\r", "").replace("\n", "").replace("\r", "")
            sline = xline.strip()
            if (len(sline) > 0):
                temp.append(sline)
    return(temp)


def lines_to_csv(all_data_lines):
    # prepare lines to save

    all_lines_to_csv = list()

    for xitem in all_data_lines:
        xline = xitem.split(",")

        dtemp = OrderedDict()
        dcount = dict()

        for x in range(1,57):
            xn = "D" + str(x).zfill(2)
            dtemp[xn] = 0
            dcount[xn] = 0
        for xxitem in xline:
            if (":" in xxitem):
                kv = xxitem.split(":")

                xname = kv[0]
                xval = float(kv[1])

                dcount[xname] = dcount[xname] + 1

                dtemp[xname] = xval

        goodline = True
        for k,v in dcount.items():
            if v > 1:
                goodline = False
                print(xline)

        if goodline:
            filepath = xitem.split(",")[-1]

            if "\\" in filepath:
                filename = filepath.split("\\")[-1]
                author = filepath.split("\\")[-3]
            elif "/" in filepath:
                filename = filepath.split("/")[-1]
                author = filepath.split("/")[-3]

            allvals = list(dtemp.values())

            result = [author] + [filename] + allvals

            all_lines_to_csv.append(result)

    return(all_lines_to_csv)

main_directory = str(sys.argv[-1])

if ":\\" in main_directory:
    if not main_directory.endswith("\\"):
        xpdir = main_directory.split("\\")[-1]
        updir = main_directory.replace(xpdir, "")
        main_directory = main_directory + "\\"

elif "/" in main_directory:
    if not main_directory.endswith("/"):
        xpdir = main_directory.split("/")[-1]
        updir = main_directory.replace(xpdir, "")
        main_directory = main_directory + "/"

abs_filepath = updir + xpdir + "_ding_results.arff"
filename = xpdir + "_ding_results.arff"
outfile = main_directory + filename[:-4] + "csv"

if ":\\" in abs_filepath:
    basename = abs_filepath.split("\\")[-1]
    xname = basename.split(".")[0]
elif "/" in abs_filepath:
    basename = abs_filepath.split("/")[-1]
    xname = basename.split(".")[0]


all_data = load_arff(abs_filepath)

all_csv_lines = lines_to_csv(all_data)

# ----------------------------------------------------------


csv_header = ["Author",
              "File",
              "D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10",
              "D11", "D12", "D13", "D14", "D15", "D16", "D17", "D18", "D19", "D20",
              "D21", "D22", "D23", "D24", "D25", "D26", "D27", "D28", "D29", "D30",
              "D31", "D32", "D33", "D34", "D35", "D36", "D37", "D38", "D39", "D40",
              "D41", "D42", "D43", "D44", "D45", "D46", "D47", "D48", "D49", "D50",
              "D51", "D52", "D53", "D54", "D55", "D56",
              ]

with io.open(outfile, "w", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
    # write header
    writer.writerow(csv_header)
    # write data
    for cline in all_csv_lines:
        writer.writerow(cline)