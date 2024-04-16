#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Please provide filename, number of processes and humans"
    exit 1
fi

shapenum=5

filename=$1
procs=$2
humans=$3

echo "STARTING PARALLEL GENERATOR FOR SHAPE $shapenum"
echo "Procs: $2"
echo ""
echo "Humans: $3"

humanpartition=$(( humans / procs))

objects=10
properties=4
range_objects="[1,2]"
range_properties="[3,4]"

min_trips=$(( humans * 6 ))

echo "Expecting $min_trips triples"

for (( i=1; i<=$procs; i++ )); do
    echo "Starting process $i ..."
    python "generator_cli.py" "$shapenum" "synthetic_data/$filename"_"$i" -p -w "$humanpartition" "$objects" "$properties" "$range_objects" "$range_properties" "$(( humanpartition * (i - 1)))" "0" "1" &
done
