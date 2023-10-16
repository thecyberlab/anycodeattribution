#!/bin/bash

main_dir="$1"
echo "$main_dir"

echo 'RUN STEP 1'
python3 -OOBRtt "abazari_attribution/0_obli_parse_ext_v2.py" "$main_dir"
wait
echo 'RUN STEP 2'
python3 -OOBRtt "abazari_attribution/1_parseInput.py" "$main_dir"
wait
echo 'RUN STEP 3'
python3 -OOBRtt "abazari_attribution/2_input2Image.py" "$main_dir"
wait
echo 'RUN STEP 4'
python3 -OOBRtt "abazari_attribution/3_ImageFeatureExtractor.py" "$main_dir"
wait

exit