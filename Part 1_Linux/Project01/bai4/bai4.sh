#!/bin/bash

INP_PATH='../data/preprocess_sample3.csv'
OUT_PATH='./ans_sample3.csv'

awk -F'@@@' '
BEGIN {
    sum = 0
}
NR!=1 {
    sum += ($5 + 0)
}
END {
    print "Tong:" sum
}' $INP_PATH > $OUT_PATH 