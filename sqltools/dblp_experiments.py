import os
import csv
from time import time 
from rdflib import Graph, ConjunctiveGraph, Namespace
from rdflib.store import NO_STORE, VALID_STORE

EX = Namespace("http://example.com/")

from TravSHACL import parse_heuristics, GraphTraversal, ShapeSchema

from slsparser.shapels import parse
from slsparser.utilities import negation_normal_form, expand_shape

from database import DatabaseInterface
from converter import ConverterInterface, Mode
from shuq.unaryquery import translate_conformance_all

root = './sqltools/' # SET ROOT HERE
source_data_dir_name = 'dblp_data'
working_dir_name = 'wd_dblp'

database_dir = f"{root}{working_dir_name}/"


def time_shape_milliseconds(loaded_db, shapefile_location, target_all=False) -> int:
    shapesgraph = Graph()
    shapesgraph.parse(shapefile_location)

    definitions, targets = parse(shapesgraph)

    conformance_sqlquery = translate_conformance_all(definitions, targets, target_all=target_all)

    start_time = int(time() * 1000)
    try:
        resultset = loaded_db.execute(conformance_sqlquery)
    except Exception as e:
        print("QUERY COULD NOT RUN")
        raise e
    end_time = int(time() * 1000)

    execution_time = end_time - start_time

    return execution_time


def run_experiments_shuq(shapeloc, source_data_filename, only_duckdb=False) -> int:
    """
    source_data_filename should simply be the name within the subfolder:
    "synthetic_data/ds_data{shapenum}/{source_data_filename}"

    The source data filename should be unique! so for example "data1_1mio", "data1_2mio", ...

    returns the query execution time in milliseconds
    """
    use_berkeley_for_duckdb=True

    source_data_dir_name = 'dblp_data'

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

    # EXPERIMENT
    print("STARTING QUERY EXECUTION...")
    print(f"FILE {shapeloc}")
    totaltime = 0
    for i in range(3):
        timing = time_shape_milliseconds(loaded_db, shapeloc, target_all=False)
        totaltime += timing
    avg = totaltime // 3
    print(f"TIME {avg}")

    return avg


def load_berkeley_graph(source_data_filename):
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


def run_experiments_travshacl(shapeloc, endpoint):
    prio_target = 'TARGET'  # shapes with target definition are preferred, alternative value: ''
    prio_degree = 'IN'  # shapes with a higher in-degree are prioritized, alternative value 'OUT'
    prio_number = 'BIG'  # shapes with many constraints are evaluated first, alternative value 'SMALL'
    
    # EXPERIMENT
    print("STARTING EXPERIMENTS...")
    print(f"FILE {shapeloc}")
    shapesgraph = Graph()
    shapesgraph.parse(shapeloc)

    shape_schema = ShapeSchema(
        schema_dir=shapesgraph,
        endpoint=endpoint,
        endpoint_user=None,  # username if validating a private endpoint
        endpoint_password=None,  # password if validating a private endpoint
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
        result = shape_schema.validate()  # validate the SHACL shape schema
        end_time = int(time() * 1000)
        timing = end_time - start_time
        totaltime += timing
    
    return totaltime // 3


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 4:
        print("type shapeloc dataloc (endpoint)")
        exit()

    type = sys.argv[1]
    shapeloc = sys.argv[2]
    dataloc = sys.argv[3]

    if type not in ['-s', '-t']: # shuq or travshacl with endpoint
        print("illigal type ", type)
        
    endpoint = None
    if type == '-t':
        endpoint = sys.argv[4]

    name = 'unknown'
    if type == '-s':
        name = 'shuq'
    elif type == '-t':
        name = 'travshacl'

    print(f"Starting shape {shapeloc}\n type {type}\n dataloc {dataloc}\n endpoint {endpoint}")
    
    timing = -1
    if type == '-s':
        timing = run_experiments_shuq(shapeloc, dataloc)
    elif type == '-t':
        timing = run_experiments_travshacl(shapeloc, endpoint)
    print("FINAL TIME: ")
    print(timing)
    print()
