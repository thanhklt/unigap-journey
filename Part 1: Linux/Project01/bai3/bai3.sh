#!/bin/bash

INP_PATH='../data/preprocess_sample1.csv'
OUT_PATH='./ans_sample1.csv'

read min_val max_val <<< "$(awk -F'@@@' '
    BEGIN {
        min_val = 1000000000
        max_val = -1
        count = 0
    }
    NR!=1 && $4 ~ /^[0-9]+$/{
        value = $5 + 0
        if (count == 0) {
            min_val = $5 + 0
            max_val = $5 + 0
        }
        else {
            if ($5 > max_val){
                max_val = $5 + 0
            }
            if ($5 < min_val) {
                min_val = $5 + 0 
            }
        }
        count += 1
    }

    END {
        print min_val, max_val
    }' $INP_PATH 
)"

echo $min_val, $max_val
awk -F'@@@' -v min="$min_val" -v max="$max_val" '
BEGIN {
    OFS = ","
}

NR != 1 && ($5 + 0 == min || $5 + 0 == max) {
    print $2, $6, $12, $5
}
' "$INP_PATH" > "$OUT_PATH"