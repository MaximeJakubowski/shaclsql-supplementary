#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Please provide filename, number of processes and humans"
    exit 1
fi

shapenum=1

filename=$1
procs=$2
humans=$3

echo "STARTING PARALLEL GENERATOR FOR SHAPE $shapenum"
echo "Procs: $2"
echo ""
echo "Humans: $3"

humanpartition=$(( humans / procs))

objects=10
prob_phone=95
prob_email=10
range_phone="[1,5]"
range_email="[1,3]"

min_trips=$(( humans * 5 ))

echo "Expecting $min_trips triples"

for (( i=1; i<=$procs; i++ )); do
    echo "Starting process $i ..."
    python "generator_cli.py" "$shapenum" "synthetic_data/$filename"_"$i" -p -w "$humanpartition" "$objects" "$prob_phone" "$prob_email" "$range_phone" "$range_email" "$(( humanpartition * (i - 1)))" "0" &
done
