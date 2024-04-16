from synthetic_experiments import load_berkeley_graph

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("USAGE: shapenum, datanum!")
        exit()

    shapenum = sys.argv[1]
    datanum = sys.argv[2]

    dataname = f"data{shapenum}_{datanum}mio"

    load_berkeley_graph(shapenum, dataname)
