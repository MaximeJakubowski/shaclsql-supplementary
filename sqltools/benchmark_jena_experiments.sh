#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Please provide mode, dataname"
    exit 1
fi

mode=$1
dataname=$2

mem="-t"

typename="jena"
type="-j"

resultfile="results/results_benchmark_"$typename"_$dataname.csv"

echo "" > $resultfile

datalocation="wd_benchmark/$dataname"_tdb/

shapes_location="benchmark_shapes_selection"
if [ "$mode" = "-t" ] ; then
    shapes_location="benchmark_shapes_dummy"
fi

for shapename in $(ls "$shapes_location") ; do
    shapefilename="$shapes_location/$shapename"
    echo $datalocation
    echo $shapefilename

    totaltiming=0
    for i in {1..3} ; do
	timing=$(java -Xmx15G -jar "jstimer/jstimer3.jar" -v $type $mem $shapefilename $datalocation)
	echo "Timing " $timing
	totaltiming=$((totaltiming + timing))
    done
    avg=$((totaltiming / 3))
    echo $dataname, $shapename, $avg  >> $resultfile
done
