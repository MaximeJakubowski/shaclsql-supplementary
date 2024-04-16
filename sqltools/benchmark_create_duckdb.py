from benchmark_experiments import run_experiments_shuq

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("USAGE: datafile!")
        exit()

    datafile = sys.argv[1]

    run_experiments_shuq(datafile, only_duckdb=True)
