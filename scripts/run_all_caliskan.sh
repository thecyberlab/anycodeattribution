#!/bin/bash

# Given a directory containing sub datasets, runs the caliskan_v2.py code 
# and formats the generated output files into a csv file using the caliskan_csv.py code

# Script is run with the command: ./run_all.sh name_of_main_dir
main_dir="$1"

echo "Caliskan start"

caliskan_code1="caliskan_attribution/caliskan1_v3.py"
caliskan_code2="caliskan_attribution/caliskan2_v3.py"
csv_file="caliskan_attribution/caliskan_cvs_v3.py"

echo $main_dir
#for dir in $main_dir/*
#do
#	if [ -d $dir ]
#	then
	echo "$main_dir"
	python3 "$caliskan_code1" "$main_dir" &
	python3 "$caliskan_code2" "$main_dir"
	python3 "$csv_file" "$main_dir"
#    fi
#done
echo "Caliskan end"

exit 0
