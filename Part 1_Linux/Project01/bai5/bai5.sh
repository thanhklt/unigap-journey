#!/bin/bash

INP_PATH='../data/preprocess_data.csv'
OUT_PATH='../cleaned_data/ans_bai5.csv'

awk -F'@@@' '
    BEGIN {
        OFS="|"
    }
    NR!=1 {
        profit = ($5+0) - ($4+0)
        print $2, $6, $12, profit
    }
' "$INP_PATH" | sort -t'|' -nr -k4,4 | head -n 10 > "$OUT_PATH"
