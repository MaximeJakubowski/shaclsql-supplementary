#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Please provide mode, size"
    exit 1
fi

mode=$1
size=$2

mem="-t"

typename="jena"
type="-j"

resultfile="results/results_synthetic_"$typename"_$size.csv"

echo "" > $resultfile

for shapenum in {1..10} ; do
    datalocation="wd_synthetic/data$shapenum"_"$size"mio"_tdb/"
    shapefilename="synthetic_shapes/shape$shapenum".ttl
    echo $datalocation
    echo $shapefilename
    totaltime=0
    for i in {1..3} ; do
	echo $i
	timing=$(java -Xmx15G -jar "jstimer/jstimer3.jar" $mode $type $mem $shapefilename $datalocation)
	totaltime=$((totaltime + timing))
    done
    avg=$((totaltime / 3))
    echo $shapenum, $avg >> $resultfile
done
