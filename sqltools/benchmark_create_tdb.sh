#!/bin/bash

for dataname in tyrol15mio ; do
    datafilename="benchmark_data/$dataname".ttl

    tdblocation="wd_benchmark/$dataname"_tdb/
    tdbloader --loc=$tdblocation $datafilename
    wait
done

