#!/bin/bash

INP_PATH='../data/preprocess_sample3.csv'
OUT_PATH='./ans_sample3.csv'

# Xu ly director
echo "Dao dien nhieu phim nhat la: " > "$OUT_PATH"
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
' $INP_PATH | sort -t'|' -k2,2 -nr | head -n 1 >> $OUT_PATH

# Xu ly dien vien
echo "Dien vien dong nhieu phim nhat la: " >> "$OUT_PATH"
awk -F'@@@' '
    BEGIN {
        OFS="|"
    }
    NR!=1 && $7 != "" {
        split($7, tmp, "|")
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
