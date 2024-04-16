import os
import csv
import pyshacltimings.timings as pstiming
from time import time
from time import sleep
from rdflib import Graph, URIRef, ConjunctiveGraph, Namespace
from rdflib.store import NO_STORE, VALID_STORE

EX = Namespace("http://example.com/")

from TravSHACL import parse_heuristics, GraphTraversal, ShapeSchema

from slsparser.shapels import parse
from slsparser.utilities import negation_normal_form, expand_shape

from database import DatabaseInterface
from converter import ConverterInterface, Mode
from shuq.unaryquery import translate_conformance_all

debug = False
debug_info = True

root = './sqltools/' # SET ROOT HERE

def time_shape_milliseconds(loaded_db, shapefile_location, target_all=False) -> int:
    shapesgraph = Graph()
    shapesgraph.parse(shapefile_location)

    definitions, targets = parse(shapesgraph)

    conformance_sqlquery = translate_conformance_all(definitions, targets, target_all=target_all)
    if debug and debug_info:
        print("QUERY")
        print(conformance_sqlquery)

    start_time = int(time() * 1000)
    try:
        resultset = loaded_db.execute(conformance_sqlquery)
    except Exception as e:
        print("QUERY COULD NOT RUN")
        raise e
    end_time = int(time() * 1000)

    execution_time = end_time - start_time

    if debug and debug_info:
        print("RESULT:")
        print(resultset)

    return execution_time


def run_experiments_shuq(shapenum, source_data_filename, only_duckdb=False, target_all=False) -> int:
    """
    source_data_filename should simply be the name within the subfolder:
    "synthetic_data/ds_data{shapenum}/{source_data_filename}"

    The source data filename should be unique! so for example "data1_1mio", "data1_2mio", ...

    returns the query execution time in milliseconds
    """
    use_berkeley_for_duckdb=True

    source_data_dir_name = f'synthetic_data/ds_data{shapenum}/'

    shapes_dir_name = 'synthetic_shapes'
    working_dir_name = 'wd_synthetic'

    shapes_dir = f"{root}{shapes_dir_name}/"
    database_dir = f"{root}{working_dir_name}/"
    database_name = f'{source_data_filename}.duckdb'

    source_data_location = root + f'{source_data_dir_name}/{source_data_filename}.ttl'

    # CREATE DATABASE
    print("LOADING DATABASE...")
    skip_db = False
    if database_name in os.listdir(database_dir):
        skip_db = True
        print(f"EXP: Using existing database: {database_name}")
    
    if not skip_db:
        print(f"EXP: Creating new database: {database_name}")
        _bdbpath = None
        if use_berkeley_for_duckdb:
            _bdbpath = database_dir + f"{source_data_filename}_berkeleydb/"
        ConverterInterface().run_converter(source_data_location, 
                                            database_dir + f'{source_data_filename}_tables_as_csv', 
                                            database_dir + database_name,
                                            Mode.TTL_TO_DB, True,
                                            berkeley=use_berkeley_for_duckdb,
                                            berkeleydbpath=_bdbpath)

    if only_duckdb:
        return -1
        
    loaded_db = DatabaseInterface(database_dir + database_name)

    # COLLECT SHAPE FILENAMES
    shapefile = f'shape{shapenum}.ttl'

    # EXPERIMENT
    print("STARTING QUERY EXECUTION...")
    print(f"FILE {shapefile}")
    totaltime = 0
    for i in range(3):
        timing = time_shape_milliseconds(loaded_db, shapes_dir + shapefile, target_all=target_all)
        totaltime += timing
    avg = totaltime // 3
    print(f"TIME {avg}")

    return avg


def load_berkeley_graph(shapenum, source_data_filename):
    source_data_dir_name = f'synthetic_data/ds_data{shapenum}/'
    working_dir_name = 'wd_synthetic'
    database_dir = f"{root}{working_dir_name}/"

    source_data_location = root + f'{source_data_dir_name}/{source_data_filename}.ttl'

    berkeleydbpath = database_dir + f"{source_data_filename}_berkeleydb/"
    datagraph = ConjunctiveGraph("BerkeleyDB")
    rt = datagraph.open(berkeleydbpath, create=False)

    print("LOADING BERKELEY DATAGRAPH...")
    if rt == NO_STORE:
        # There is no underlying BerkeleyDB infrastructure, so create it
        print("Creating new BerkeleyDB")
        datagraph.open(berkeleydbpath, create=True)
        datagraph.parse(source_data_location)
        datagraph.commit()
        print(f"Triples in data graph {source_data_filename}: {len(datagraph)}")
    else:
        print("Using existing BerkeleyDB")
        assert rt == VALID_STORE, "The underlying BerkeleyDB store is corrupt"

    print(f"Triples still in data graph: {len(datagraph)}")
    return datagraph


def load_memory_graph(shapenum, source_data_filename):
    source_data_dir_name = f'synthetic_data/ds_data{shapenum}/'
    source_data_location = root + f'{source_data_dir_name}/{source_data_filename}.ttl'

    print("LOADING MEMORY DATAGRAPH...")
    datagraph = ConjunctiveGraph()
    datagraph.parse(source_data_location) 
    print(f"Triples in data graph: {len(datagraph)}")
    return datagraph


def run_experiments_travshacl(shapenum, source_data_filename, endpoint):
    prio_target = 'TARGET'  # shapes with target definition are preferred, alternative value: ''
    prio_degree = 'IN'  # shapes with a higher in-degree are prioritized, alternative value 'OUT'
    prio_number = 'BIG'  # shapes with many constraints are evaluated first, alternative value 'SMALL'

    shapes_dir_name = 'synthetic_shapes_travshacl'
    shapes_dir = f"{root}{shapes_dir_name}/"

    # COLLECT SHAPE FILENAMES
    shapefile = f"shape{shapenum}.ttl"
    
    # EXPERIMENT
    print("STARTING EXPERIMENTS...")
    print(f"FILE {shapes_dir}{shapefile}")
    shapesgraph = Graph()
    shapesgraph.parse(shapes_dir + shapefile)

    sleep(1)
    shape_schema = ShapeSchema(
        schema_dir=shapesgraph,
        endpoint=endpoint,
        graph_traversal=GraphTraversal.DFS,
        heuristics=parse_heuristics(prio_target + ' ' + prio_degree + ' ' + prio_number),
        use_selective_queries=True,
        max_split_size=256,
        order_by_in_queries=False,  # sort the results of SPARQL queries in order to ensure the same order across several runs
        save_outputs=False  # save outputs to output_dir, alternative value: False
    )

    totaltime = 0
    for i in range(3):
        start_time = int(time() * 1000)
        shape_schema.validate()  # validate the SHACL shape schema
        end_time = int(time() * 1000)
        timing = end_time - start_time
        totaltime += timing
        print(f"TIME RUN {shapenum}", timing)
        sleep(10)
    
    return totaltime // 3


if __name__ == '__main__':
    import sys
    # data_nums = [1,2,3,4,5]
    # extra_data_nums = [10,15,20]

    if len(sys.argv) < 3:
        print("datanum, type, (endpoint), shapenums!")
        exit()

    data_num = sys.argv[1]

    type = sys.argv[2]
    if type not in ['-s', '-t']: # shuq or pyshacl or travshacl with endpoint
        print("illigal type ", type)

    shapenums = sys.argv[3:]
        
    endpoint = None
    if type == '-t':
        shapenums = sys.argv[4:] # we do not want the endpoint as datanums
        endpoint = sys.argv[3]

    target_all = False
    if shapenums[-1] == 'a':
        target_all = True
        shapenums = shapenums[:-1]

    name = 'unknown'
    if type == '-s':
        name = 'shuq'
    elif type == '-t':
        name = 'travshacl'

    print(f"Starting shape {shapenums}, type {type}, data_nums {data_num}{f', endpoint {endpoint}' if endpoint else ''}")
    
    result_filename = f'results/results_synthetic_{name}_{data_num}.csv'
    with open(result_filename, 'w') as resultfile:
        writer = csv.writer(resultfile)
        timelog = {}
        for shapenum in shapenums:
            dataname = f"data{shapenum}_{data_num}mio"
            if shapenum == "7":
                dataname = f"data6_{data_num}mio"
            timing = -1
            if type == '-s':
                timing = run_experiments_shuq(shapenum, dataname, target_all=target_all)
            elif type == '-t':
                print(shapenum, dataname, endpoint)
                timing = run_experiments_travshacl(shapenum, dataname, endpoint + f'/data{shapenum}')
            writer.writerow([dataname, timing])
