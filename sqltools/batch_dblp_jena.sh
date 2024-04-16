#!/bin/bash


dataloc="wd_dblp/dblp2022-2023_tdb/"

resultfile="results/results_dblp2022-2023_jena.csv"

echo "" > $resultfile

for shape in personshape.ttl publicationshape.ttl teamplayershape.ttl ;	do
    shapeloc="dblp_shapes/$shape"
    totaltime=0
    for i in {1..3} ; do
        echo $i
        timing=$(java -Xmx15G -jar "jstimer/jstimer3.jar" -v -j -t $shapeloc $dataloc)
	totaltime=$((totaltime + timing))
    done
    avg=$((totaltime / 3))
    echo $shape, $avg >> $resultfile
done

