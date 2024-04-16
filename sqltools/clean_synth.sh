#!/bin/bash

synnum=$1

cd synthetic_data/ds_data${synnum}/

for i in *.ttl_1 ; do
    echo $i
    mv -v $i ${i%.ttl_1}.ttl
done

