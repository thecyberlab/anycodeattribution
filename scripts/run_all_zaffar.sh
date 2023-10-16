#!/bin/bash

main_dir="$1"
echo $main_dir
echo 'RUN STEP 1'
python -OOBRtt "zaffar_attribution/0_prepare_v3.py" "$main_dir" > $main_dir"_0.txt" 2>&1
wait
echo 'RUN STEP 2'
python -OOBRtt "zaffar_attribution/1_parseInput.py" $main_dir > $main_dir"_1.txt" 2>&1
wait
echo 'RUN STEP 3'
python -OOBRtt "zaffar_attribution/2_input2Image.py" $main_dir > $main_dir"_2.txt" 2>&1
wait
echo 'RUN STEP 4'
python -OOBRtt "zaffar_attribution/3_ImageFeatureExtractor.py" $main_dir > $main_dir"_3.txt" 2>&1
wait
echo 'RUN STEP 5'
python -OOBRtt "zaffar_attribution/4_Classification_RF.py" $main_dir > $main_dir"_4.txt" 2>&1



