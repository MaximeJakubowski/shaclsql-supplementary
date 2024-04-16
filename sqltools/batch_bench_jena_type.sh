#!/bin/bash

resultfile="results/large_graph_jena_dummy.csv"

for shapename in $(ls benchmark_shapes_dummy) ; do
    shapefilename="benchmark_shapes_dummy/$shapename"
    totaltiming=0
    echo "Running $shapename ..."
    for i in {1..3} ; do
	timing=$(java -Xmx15G -jar "jstimer/jstimer3.jar" -v -j -t $shapefilename wd_benchmark/large_graph_tdb )
	totaltiming=$((totaltiming + timing))
    done
    avg=$((totaltiming / 3))
    echo "Time avg 3 runs: $avg"
    echo $shapename, $avg >> $resultfile
done
