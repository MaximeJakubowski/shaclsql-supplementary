from synthetic_experiments import run_experiments_shuq

if __name__ == '__main__':
    import sys
    data_nums = [1,2,3,4,5,10,15,20]

    if len(sys.argv) != 3:
        print("USAGE: shapenum, datanum!")
        exit()

    shapenum = sys.argv[1]
    datanum = sys.argv[2]

    dataname = f"data{shapenum}_{datanum}mio"

    run_experiments_shuq(shapenum, dataname, only_duckdb=True)
