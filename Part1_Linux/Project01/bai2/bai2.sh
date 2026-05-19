#!/bin/bash

INP_PATH="../data/preprocess_data.csv"
OUT_PATH="../cleaned_data/cleaned_data2.csv"

awk -F'@@@' 'NL!=1 && $18 > 7.5{print $2, $6, $12, $18}' $INP_PATH | sort -k4,4nr > $OUT_PATH