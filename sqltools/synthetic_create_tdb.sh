#!/bin/bash

# script to create Jena tdb2 database files to use for TravSHACL and Bare SPARQL experiments

for shapenum in 1 2 3 5 6 ; do
    for size in 5 ; do
	dataname="data$shapenum"_"$size"mio
	datafilename="synthetic_data/ds_data$shapenum/$dataname".ttl

	tdblocation="wd_synthetic/$dataname"_tdb/
	tdbloader --loc=$tdblocation $datafilename
	wait
    done
done

