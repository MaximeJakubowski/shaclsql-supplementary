#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Please provide filename, number of processes and humans"
    exit 1
fi

shapenum=3

filename=$1
procs=$2
humans=$3

echo "STARTING PARALLEL GENERATOR FOR SHAPE $shapenum"
echo "Procs: $2"
echo ""
echo "Humans: $3"

companies=10
friends=100
range_friends="[1,4]"
range_companies="[0,2]"

humanpartition=$(( humans / procs ))

min_trips=$(( humans * 4 ))

echo "Expecting $min_trips triples"

for (( i=1; i<=$procs; i++ )); do
    echo "Starting process $i ..."
    python "generator_cli.py" "$shapenum" "synthetic_data/$filename"_"$i" -p -w "$humanpartition" "$friends" "$companies" "$range_friends" "$range_companies" "$(( humanpartition * (i - 1)))" "0" "0" &
done


