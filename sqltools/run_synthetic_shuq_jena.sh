for i in 10 15 ; do
    echo "STARTING JENA 10"
    bash synthetic_java_experiments.sh -j $i
    wait
    sleep 10
    echo "STARTING SHUQ"
    python synthetic_experiments.py $i -s 1 2 3 4 5 6 7 8 9 10
    sleep 10
done

python synthetic_experiments.py 20 -s 1 2 3 4 5 6 7 8 9 10
