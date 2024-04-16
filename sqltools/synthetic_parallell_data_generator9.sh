#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Please provide filename, number of processes and humans"
    exit 1
fi

shapenum=9

filename=$1
procs=$2
humans=$3

echo "STARTING PARALLEL GENERATOR FOR SHAPE $shapenum"
echo "Procs: $2"
echo ""
echo "Humans: $3"

humanpartition=$(( humans / procs))

objects=200
langs=20
range_objects="[1,3]"

min_trips=$(( humans * 3 ))

echo "Expecting $min_trips triples"

for (( i=1; i<=$procs; i++ )); do
    echo "Starting process $i ..."
    python "generator_cli.py" "$shapenum" "synthetic_data/$filename"_"$i" -p -w "$humanpartition" "$objects" "$langs" "$range_objects" "$(( humanpartition * (i - 1)))" "0" &
done
