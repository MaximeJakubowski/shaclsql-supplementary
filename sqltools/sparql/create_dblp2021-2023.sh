#!/bin/bash

year="2021-2023"
personname="person$year"
pubname="pubs$year"

rsparql --service http://localhost:3030/dblp --query "dblp_$pubname".rq > "../dblp_data/$pubname".ttl

wait

rsparql --service http://localhost:3030/dblp --query "dblp_$personname".rq > "../dblp_data/$personname".ttl

wait

cd ../dblp_data

cp "$pubname".ttl "dblp$year".ttl

tail --lines=+5 "$personname".ttl >> "dblp$year".ttl
