#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Please provide filename, number of processes and humans"
    exit 1
fi

shapenum=2

filename=$1
procs=$2
humans=$3

echo "STARTING PARALLEL GENERATOR FOR SHAPE $shapenum"
echo "Procs: $2"
echo ""
echo "Humans: $3"

humanpartition=$(( humans / procs))

managers=10
range_manhum="[3,5]"

min_trips=$(( humans * 3 ))
max_trips=$(( humans * 5 ))

echo "Expecting minimal $min_trips triples"
echo "Expecting maximal $max_trips triples"

for (( i=1; i<=$procs; i++ )); do
    echo "Starting process $i ..."
    python "generator_cli.py" "$shapenum" "synthetic_data/$filename"_"$i" -p -w "$humanpartition" "$managers" "$range_manhum" "$(( humanpartition * (i - 1)))" "0" &
done


