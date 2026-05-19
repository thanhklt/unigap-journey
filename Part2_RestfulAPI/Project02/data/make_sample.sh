#!/bin/bash

head -n 1 products-0-200000.csv > $1
tail -n +2 products-0-200000.csv | shuf -n $2 >> $1