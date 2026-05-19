#!/bin/bash

INP_PATH='../data/preprocess_data.csv'
OUT_PATH='../cleaned_data/ans_bai7.csv'

awk -F'@@@' '
    BEGIN {
        OFS="|"
    }
    NR!=1 && $14 != ""{
        split($14, tmp, "|")
        for (i in tmp) {
            gsub(/^ +| +$/, "", tmp[i])
            genres[tmp[i]] += 1
        }
    }
    END {
        for (genre in genres){
            print genre, genres[genre]
        }
    }
' "$INP_PATH" > "$OUT_PATH"