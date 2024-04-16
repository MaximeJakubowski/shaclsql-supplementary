bash batch_synth_shuq.sh
wait

bash batch_synth_jena.sh
wait

fuseki-server --config=fuseki-config.ttl &
sleep 30

bash batch_synth_travshacl.sh
