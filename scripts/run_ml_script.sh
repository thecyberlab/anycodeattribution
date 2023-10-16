#!/bin/bash

main_dir="$1"
feature_1="$2"
feature_2="$3"
feature_3="$4"
feature_4="$5"
feature_5="$6"

echo "Starting ML script"
if [ ! -z "$feature_1" ]; then
  python3 -OOBRtt "ml_jupyter_scripts/ml_script_runner.py" "$main_dir" "$feature_1"
fi
wait
if [ ! -z "$feature_2" ]; then
  python3 -OOBRtt "ml_jupyter_scripts/ml_script_runner.py" "$main_dir" "$feature_2"
fi
wait
if [ ! -z "$feature_3" ]; then
  python3 -OOBRtt "ml_jupyter_scripts/ml_script_runner.py" "$main_dir" "$feature_3"
fi
wait
if [ ! -z "$feature_4" ]; then
  python3 -OOBRtt "ml_jupyter_scripts/ml_script_runner.py" "$main_dir" "$feature_4"
fi
wait
if [ ! -z "$feature_5" ]; then
  python3 -OOBRtt "ml_jupyter_scripts/ml_script_runner.py" "$main_dir" "$feature_5"
fi
wait