#!/bin/bash

for shape in personshape.ttl publicationshape.ttl teamplayershape.ttl ; do
    shapeloc="dblp_shapes/$shape"
    python dblp_experiments.py -s $shapeloc dblp2022-2023
done
