#!/bin/bash

INP_PATH='../data/preprocess_data.csv'
OUT_PATH='../cleaned_data/ans_bai6.csv'

# Xu ly director
awk -F'@@@' '
    BEGIN {
        OFS="|"
    }
    NR!=1 && $9 != ""{
        directors[$9]+=1
    }
    END {
        for (director in directors) {
            print director, directors[director]
        }
    }
' $INP_PATH | sort -t'|' -k2,2 -nr | head -n 1 > $OUT_PATH

# Xu ly dien vien
awk -F'@@@' '
    BEGIN {
        OFS="|"
    }
    NR!=1 && $7 != "" {
        split($7, tmp, ",")
        for (i in tmp) {
            gsub(/^ +| +$/, "", tmp[i])
            actors[tmp[i]] += 1
        }
    }
    END {
        for (actor in actors) {
            print actor, actors[actor]
        }
    }
' $INP_PATH | sort -t'|' -k2,2 -nr | head -n 1 >> $OUT_PATH
