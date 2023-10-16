#!/bin/bash

main_dir="$1"

echo "-----------"
echo "PARSING --> "$main_dir""

#exit

echo 'RUN STEP 1'
python3 -OOBRtt "kothari_attribution/kothari_v3_1.py" "$main_dir"
wait
echo 'RUN STEP 2'
python3 -OOBRtt "kothari_attribution/kothari_v3_2_+.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_2_0-9.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_2_a-d.py" "$main_dir" &
wait
python3 -OOBRtt "kothari_attribution/kothari_v3_2_e-h.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_2_i-l.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_2_m-p.py" "$main_dir" &
wait
python3 -OOBRtt "kothari_attribution/kothari_v3_2_q-t.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_2_u-x.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_2_y-z.py" "$main_dir" &
wait
echo 'RUN STEP 3'
python3 -OOBRtt "kothari_attribution/kothari_v3_3.py" "$main_dir"
wait
echo 'RUN STEP 4'
python3 -OOBRtt "kothari_attribution/kothari_v3_4_+.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_4_0-9.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_4_a-d.py" "$main_dir" &
wait
python3 -OOBRtt "kothari_attribution/kothari_v3_4_e-h.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_4_i-l.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_4_m-p.py" "$main_dir" &
wait
python3 -OOBRtt "kothari_attribution/kothari_v3_4_q-t.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_4_u-x.py" "$main_dir" &
python3 -OOBRtt "kothari_attribution/kothari_v3_4_y-z.py" "$main_dir" &
wait

echo 'RUN STEP 4A - AGGREGATING ARFF FILES'
cat "$main_dir"/kothari_?-?.arff "$main_dir"/kothari_0-9.arff "$main_dir"/kothari_a-d.arff "$main_dir"/kothari_e-h.arff "$main_dir"/kothari_i-l.arff "$main_dir"/kothari_m-p.arff "$main_dir"/kothari_q-t.arff "$main_dir"/kothari_u-x.arff "$main_dir"/kothari_y-z.arff | LC_ALL=C sort | LC_ALL=C uniq > "$main_dir"/kothari.arff
wait

wait
echo 'RUN STEP 5'
python3 -OOBRtt "kothari_attribution/kothari_v3_5.py" "$main_dir"
wait

wait
echo "DONE"
exit