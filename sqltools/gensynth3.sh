#!/bin/bash


synnum=$1 # the shape number
base=$2 # the 1 mio number

for i in 1 2 3 4 5 10 15 20 ; do
    numhum=$((base * i * 1000))
    bash "synthetic_parallell_data_generator$synnum.sh" "ds_data$synnum/data$synnum"_"${i}mio.ttl" 1 "$numhum"
done
