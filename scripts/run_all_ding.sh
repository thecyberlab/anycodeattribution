#!/bin/bash

# Given a directory containing sub datasets, runs the ding_v3.py code 
# and formats the generated output files into a csv 

# Script is run with the command: ./run_all.sh name_of_main_dir
main_dir="$1"
# file_name="$2"

ding_code="ding_attribution/ding_v4.py"
csv_file="ding_attribution/ding_csv.py"

for dir in $main_dir/*
do
	if [ -d $dir ]
	then
		python3 "$ding_code" "$dir"
		wait
		python3 "$csv_file" "$dir"
	fi
done

# Extract the last directory using the `basename` command
file_name=$(basename "$main_dir")

# WRITE
echo "Author,File,D01,D02,D03,D04,D05,D06,D07,D08,D09,D10,D11,D12,D13,D14,D15,D16,D17,D18,D19,D20,D21,D22,D23,D24,D25,D26,D27,D28,D29,D30,D31,D32,D33,D34,D35,D36,D37,D38,D39,D40,D41,D42,D43,D44,D45,D46,D47,D48,D49,D50,D51,D52,D53,D54,D55,D56" > ""$main_dir"/"$file_name"_ding_results.csv"

find "$main_dir" -name "*.csv" -print0 | xargs -0 cat | grep -v "Author,File" >> ""$main_dir"/"$file_name"_ding_results.csv"

exit 0
