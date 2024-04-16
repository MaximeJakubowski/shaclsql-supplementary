for shape in 4 5 6 8 9 10 ; do
    for size in 10 15 ; do
        python synthetic_create_duckdb.py $shape $size
        wait
    done    
done