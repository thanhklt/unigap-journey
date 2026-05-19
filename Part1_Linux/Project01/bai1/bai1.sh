#!/bin/bash

INP_PATH="./sample1.csv"
OUT_PATH="./cleaned_sample1.csv"

function convert {
    day=$(echo $1 | cut -d'/' -f2)
    month=$(echo $1 | cut -d '/' -f1)
    year=$(echo $1| cut -d '/' -f3)
    if [ "$year" -lt 15 ]; then
        year="20$year"
    else
        year="19$year"
    fi
    month=$(printf "%02d" "$month")
    day=$(printf "%02d" "$day")

    echo "$year$month$day"
}

function clean {
    head -n 1 "$1" > "$2"

    tail -n +2 "$1" | while read line
    do
        date_value=$(echo "$line" | grep -oE '([0-9])+/([0-9])+/([0-9])+')
        if [ -n "$date_value" ]; then
            formatted=$(convert "$date_value") 
        fi
        printf "%s\t%s\n" "$formatted" "$line"
    done | sort -r  >> "$2"
}

# Main
INP_PATH="../data/data.csv"
OUT_PATH="../cleaned_data/cleaned_data1.csv"
clean $INP_PATH $OUT_PATH
