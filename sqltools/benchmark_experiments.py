import os
import csv
import pyshacltimings.timings as pstiming
from time import time, sleep
from rdflib import Graph, URIRef, ConjunctiveGraph
from rdflib.store import NO_STORE, VALID_STORE

from TravSHACL import parse_heuristics, GraphTraversal, ShapeSchema

from slsparser.shapels import parse
from slsparser.utilities import negation_normal_form, expand_shape

from database import DatabaseInterface
from converter import ConverterInterface, Mode
from shuq.unaryquery import translate_conformance_all

debug = False
debug_shapename = 'EventShape'
debug_info = False

debug_full_shapename = URIRef('http://gdb.benchmark.com/' + debug_shapename)
debug_filename = debug_shapename.lower() + '.ttl'

trials=3

root = './sqltools/' # SET ROOT HERE
source_data_dir_name = 'benchmark_data'

shapes_dir_name = 'benchmark_shapes_selection'
working_dir_name = 'wd_benchmark'

skiptests = []

def time_shape_milliseconds(loaded_db, shapefilename, target_all=False) -> int:
    shapesgraph = Graph()
    shapesgraph.parse(shapefilename)

    definitions, targets = parse(shapesgraph)

    if debug and debug_info:
        print("SHAPE")
        print(negation_normal_form(
            expand_shape(definitions, definitions[debug_full_shapename])
        ))

    conformance_sqlquery = translate_conformance_all(definitions, targets)

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


def run_experiments_shuq(source_data_filename, target_all=False, only_duckdb=False):
    source_data_location = root + f'{source_data_dir_name}/{source_data_filename}.ttl'
    database_dir = root + working_dir_name + '/' 
    database_name = f'{source_data_filename}.duckdb'

    if target_all:
        print("TARGET TYPES")
        shapes_dir_name = 'benchmark_shapes_dummy'
    
    timinglog = dict()

    # CREATE DATABASE
    print("LOADING DATABASE...")
    skip_db = False
    if database_name in os.listdir(database_dir):
        skip_db = True
        print(f"EXP: Using existing database: {database_name}")
    
    if not skip_db:
        print(f"EXP: Creating new database: {database_name}")
        ConverterInterface().run_converter(source_data_location, 
                                            database_dir + f'{source_data_filename}_tables_as_csv', 
                                            database_dir + database_name,
                                            Mode.TTL_TO_DB, True,
                                            berkeley=True,
                                            berkeleydbpath=database_dir + f"{source_data_filename}_berkeleydb/")

    if only_duckdb:
        return
        
    loaded_db = DatabaseInterface(database_dir + database_name)

    # COLLECT SHAPE FILENAMES
    shapefile_dir = root + f'{shapes_dir_name}/'
    shapefilenames = list(os.listdir(shapefile_dir))

    # EXPERIMENT
    print("STARTING EXPERIMENTS...")
    for shapefile in shapefilenames:
        if shapefile in skiptests:
            continue
        if debug and shapefile != debug_filename:
            continue
        print(f"FILE {shapefile_dir}{shapefile}")
        timing = 0
        for i in range(trials):
            try:
                timing += time_shape_milliseconds(loaded_db, shapefile_dir + shapefile)
            except Exception as e:
                break
        sleep(5)
        timinglog[shapefile] = timing // 3
        print(f"AVG TIME {trials} TRIALS: {timing // 3}")
    
    if debug:
        return
    
    result_filename = f'results/results_shuq_{source_data_filename.lower()}.csv'
    with open(result_filename, 'w') as resultfile:
        writer = csv.writer(resultfile)
        for key, value in timinglog.items():
            writer.writerow([key, value])


def load_berkeley_graph(source_data_filename):
    source_data_location = root + f'{source_data_dir_name}/{source_data_filename}.ttl'
    database_dir = root + working_dir_name + '/' 

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
        print(f"Triples in data graph: {len(datagraph)}")
    else:
        print("Using existing BerkeleyDB")
        assert rt == VALID_STORE, "The underlying BerkeleyDB store is corrupt"

    print(f"Triples still in data graph: {len(datagraph)}")
    return datagraph


def load_memory_graph(source_data_filename):
    source_data_location = root + f'{source_data_dir_name}/{source_data_filename}.ttl'
    print("LOADING MEMORY DATAGRAPH...")
    datagraph = ConjunctiveGraph()
    datagraph.parse(source_data_location) 
    print(f"Triples in data graph: {len(datagraph)}")
    return datagraph


def run_experiments_pyshacl(source_data_filename, datastore="memory"):
    timinglog = dict()

    if datastore == "berkeley":
        datagraph = load_berkeley_graph(source_data_filename)
    else:
        datagraph = load_memory_graph(source_data_filename)

    # COLLECT SHAPE FILENAMES
    shapefile_dir = root + shapes_dir_name + '/'
    shapefilenames = list(os.listdir(shapefile_dir))

    # EXPERIMENT
    print("STARTING EXPERIMENTS...")
    for shapefile in shapefilenames:
        if shapefile in skiptests:
            continue
        if debug and shapefile != debug_filename:
            continue
        print(f"FILE {shapefile}")
        shapesgraph = Graph()
        shapesgraph.parse(shapefile_dir + shapefile)
        timing = pstiming.Validator.time_validate(datagraph, shapesgraph)
        timinglog[shapefile] = timing
        print(f"TIME {timing}")
    
    datagraph.close()

    result_filename = f'results/results_pyshacl_{source_data_filename.lower()}.csv'
    with open(result_filename, 'w') as resultfile:
        writer = csv.writer(resultfile)
        for key, value in timinglog.items():
            writer.writerow([key, value])


def run_experiments_travshacl(source_data_filename, endpoint, target_all=False):
    prio_target = 'TARGET'  # shapes with target definition are preferred, alternative value: ''
    prio_degree = 'IN'  # shapes with a higher in-degree are prioritized, alternative value 'OUT'
    prio_number = 'BIG'  # shapes with many constraints are evaluated first, alternative value 'SMALL'

    shapes_dir_name = 'benchmark_shapes_travshacl'
    shapes_dir = f"{root}{shapes_dir_name}/"

    # COLLECT SHAPE FILENAMES
    shapefile_dir = root + shapes_dir_name + '/'
    shapefilenames = list(os.listdir(shapefile_dir))
    
    # EXPERIMENT
    timings = {}
    print("STARTING EXPERIMENTS...")
    for shapefile in shapefilenames:
        if shapefile in skiptests:
            continue
        if debug and shapefile != debug_filename:
            continue

        print(f"FILE {shapes_dir + shapefile}")
        shapesgraph = Graph()
        shapesgraph.parse(shapes_dir + shapefile)

        shape_schema = ShapeSchema(
            schema_dir=shapesgraph,
            endpoint=endpoint + shapefile,
            endpoint_user=None,  # username if validating a private endpoint
            endpoint_password=None,  # password if validating a private endpoint
            graph_traversal=GraphTraversal.DFS,
            heuristics=parse_heuristics(prio_target + ' ' + prio_degree + ' ' + prio_number),
            use_selective_queries=True,
            max_split_size=256,
            order_by_in_queries=False,  # sort the results of SPARQL queries in order to ensure the same order across several runs
            save_outputs=False
        )
        timing = 0
        for i in range(trials):
            start_time = int(time() * 1000)
            shape_schema.validate()  # validate the SHACL shape schema
            end_time = int(time() * 1000)
            timing += (start_time - end_time)
            sleep(5)
        timings[shapefile] = timing // 3
        print(f"AVG TIME {trials} TRIALS: {timing // 3}")
        
    result_filename = f'results/results_travshacl_{source_data_filename.lower()}.csv'
    with open(result_filename, 'w') as resultfile:
        writer = csv.writer(resultfile)
        for key, value in timings.items():
            writer.writerow([key, value])


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("datasetname, type, (endpoint)")
        exit()
        
    datasetname = sys.argv[1]
    type = sys.argv[2]
    
    if type not in ['-s', '-sa', '-t']: # shuq or pyshacl or travshacl with endpoint
        print("illegal type ", type)

    endpoint = None
    if type == '-t':
        endpoint = sys.argv[3]

    timelog = {}
    timing = -1
    if type == '-s':
        timing = run_experiments_shuq(datasetname)
    elif type == '-sa':
        timing = run_experiments_shuq(datasetname, target_all=True)
    elif type == '-t':
        timing = run_experiments_travshacl(datasetname, endpoint)
