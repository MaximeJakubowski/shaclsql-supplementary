# This script runs the SHACL test suite against our SHACL-SQL translation

from rdflib import Graph, RDF, SH
from rdflib.namespace import Namespace
from rdflib.term import Node
from rdflib.collection import Collection
from rdflib.paths import SequencePath

from typing import List, Set

from converter import ConverterInterface, Mode
from slsparser.shapels import parse
from slsparser.utilities import negation_normal_form, expand_shape
from database import DatabaseInterface

from shuq.unaryquery import translate_conformance_all

MF = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")
SHT = Namespace("http://www.w3.org/ns/shacl-test#")

root = "./sqltools/" # SET ROOT HERE
root_manifest_file = root + "core_test_suite/manifest.ttl"

skiptests = ['complex_shacl-shacl', # advanced paths
             'node_minInclusive-002', # datetime inclusives
             'node_minInclusive-003', # datetime inclusives
             'path_path-alternative-001', # advanced paths
             'path_path-complex-001', # advanced paths
             'path_path-complex-002', # advanced paths
             'path_path-oneOrMore-001', # advanced paths
             'path_path-sequence-001', # advanced paths
             'path_path-sequence-002', # advanced paths
             'path_path-sequence-duplicate-001', # advanced paths
             'path_path-strange-001', # advanced paths
             'path_path-strange-002', # advanced paths
             'path_path-unused-001', # advanced paths
             'path_path-zeroOrMore-001', # advanced paths
             'path_path-zeroOrOne-001']  # advanced paths


unsupported = ['misc_deactivated-001', # not supported deactivation feature
               'node_class-001', # mostly ok, we do not support subclassof for class constraint
               'node_class-003', # mostly ok, we do not support subclassof for class constraint
               'node_datatype-001', # mostly ok, we do not support ill-formed datatype checks (eg, "aa"^^xsd:integer should not validate as an integer) 
               'node_xone-duplicate', # artifact, ignore
               'property_class-001', # mostly ok, we do not support subclassof for class constraint
               'property_languageIn-001', # mostly ok, we do not support languageIn SPARQL LangMatches comparison
               'property_lessThan-001', # TODO find better query: ValidResource2 is wrongly selected as violation
               'property_lessThanOrEquals-001', # TODO same as previous (will be resolved automatically)
               'property_property-001', # here our definition of violations does not correspond with the recommendation. however, we are correct in our sense
               'property_uniqueLang-002', # ??
               'targets_targetClassImplicit-001' # we do not support advanced implicit class
               ]

skiptests += unsupported

class ValidateInfo:
    def __init__(self, path_to_validatenodegraph: str, graph: Graph, validatenode: Node, 
                 datagraph_path: str, shapesgraph_path: str, conforms: bool, violaters: Set[Node]):
        self.path_to_validatenodegraph = path_to_validatenodegraph
        self.graph = graph
        self.validatenode = validatenode
        self.datagraph_path = datagraph_path
        self.shapesgraph_path = shapesgraph_path
        self.conforms = conforms
        self.violaters = violaters

class TestReport:
    def __init__(self, basename, vinfo, resultset):
        self.basename = basename
        self.vinfo: ValidateInfo = vinfo
        self.resultset = resultset

# 1. Collect recursively all ValidateInfo
def collect_validateinfo(graphfilename: str) -> List[ValidateInfo]:
    print("CONSIDERING FILE:")
    print(graphfilename)

    vinfos: List[ValidateInfo] = []

    graph = Graph()
    try:
        graph.parse(graphfilename)
    except ValueError:
        print("ERROR PARSING! SKIP...")
        return []

    if (None, RDF.type, MF.Manifest) not in graph:
        return []
    
    # There should only be 1 manifest node
    manifest_node = list(graph.subjects(RDF.type, MF.Manifest))[0]

    include_nodes = list(graph.objects(manifest_node, MF.include))

    for node in include_nodes:
        vinfos += collect_validateinfo(str(node))

    entry_rdflists = list(graph.objects(manifest_node, MF.entries))
    if entry_rdflists:
        # there should only be one entry collection (rdf list)
        entry_nodes = list(Collection(graph, entry_rdflists[0]))

        for vnode in entry_nodes:
            datagraphpath = _extract_datagraphpath(graph, vnode)
            shapesgraphpath = _extract_shapesgraphpath(graph, vnode)
            conforms = _extract_conforms(graph, vnode)

            violaters = _extract_violaters(graph, vnode)
            
            vinfos.append(ValidateInfo(graphfilename, graph, vnode, 
                                       datagraphpath, shapesgraphpath, 
                                       conforms, violaters))

    return vinfos


def _extract_datagraphpath(graph, vnode):
    # value of: mf:action sht:dataGraph
    return str(list(graph.objects(vnode, SequencePath(MF.action, SHT.dataGraph)))[0])

def _extract_shapesgraphpath(graph, vnode):
    # value of: mf:action sht:shapesGraph
    return str(list(graph.objects(vnode, SequencePath(MF.action, SHT.shapesGraph)))[0])

def _extract_conforms(graph, vnode):
    # value of: mf:result sh:conforms
    return bool(list(graph.objects(vnode, SequencePath(MF.result, SH.conforms)))[0])

def _extract_violaters(graph, vnode) -> Set[Node]:
    # value of: mf:result sh:result sh:focusNode
    return set(graph.objects(vnode, SequencePath(MF.result, SH.result, SH.focusNode)))





debug = False 
debug_basename = 'targets_targetClassImplicit-001'
debug_shapename = None
def execute_tests(vinfos: List[ValidateInfo]):
    report: List[TestReport] = []
    querylog = {}
    shapelog = {}
    for vinfo in vinfos:
        # 1. Create the database    
        folder_name = vinfo.path_to_validatenodegraph.split('/')[-2]
        file_name =  vinfo.path_to_validatenodegraph.split('/')[-1].split('.')[0]

        EX = Namespace(f"http://datashapes.org/sh/tests/core/{folder_name}/{file_name}.test#")

        basename = folder_name + '_' + file_name
        
        if basename in skiptests:
            continue
        if debug and basename != debug_basename:
            continue
        print(f"STARTING MANIFEST: {vinfo.path_to_validatenodegraph}")
        print(vinfo.path_to_validatenodegraph)    

        dirname = basename + '/'
        databasefilename = basename + ".duckdb"
        print(databasefilename)
        ConverterInterface().run_converter(vinfo.datagraph_path[7:], 
                                           root + "wd_core_test_suite/" + dirname, 
                                           root + "wd_core_test_suite/" + dirname + databasefilename,
                                           Mode.TTL_TO_DB,
                                           True)
        
        # 1. 

        # 2. Translate the shape to conformance SQL
        # 2.a Parse to sls schema
        shapesgraph = Graph()
        shapesgraph.parse(vinfo.shapesgraph_path)

        definitions, targets = parse(shapesgraph)

        # 2.b Translate to SQL conformance query
        conformance_sqlquery = translate_conformance_all(definitions, targets)

        if debug and debug_shapename is not None:
            shapelog[basename] = negation_normal_form(
                expand_shape(definitions, definitions[EX[debug_shapename]]))
        querylog[basename] = conformance_sqlquery
        # 3. Execute query on duckdb database
        print("EXECUTING...")
        try:
            resultset = DatabaseInterface(root + "wd_core_test_suite/" + dirname + databasefilename)\
                .execute(conformance_sqlquery)
        except Exception as e:
            print("QUERY COULD NOT RUN")
            if debug and debug_basename:
                print(shapelog[basename])
            print(querylog[basename])
            raise e

        print("RESULT:")
        print(resultset)
        conforms = len(resultset) == 0

        # 4. Check if correct result
        certainly_fail = vinfo.conforms != conforms or len(vinfo.violaters) != len(resultset)
        if certainly_fail:
            report.append(TestReport(basename, vinfo, resultset))

        print(f"CORRECTNESS: {'OK' if not certainly_fail else 'FAIL'}")

    print("FAILED TEST REPORT:") 
    for tr in report:
        print(tr.basename)
        if debug:
            if debug_shapename:
                print("SHAPE:")
                print(shapelog[tr.basename])
            print("QUERY:")
            print(querylog[tr.basename])
            print("ANSWER:")
            print(tr.resultset)
            print("EXPECTED:")
            for violation in tr.vinfo.violaters:
                print(violation)

    print(f"FRACTION FAILS: {len(report)}/{len(vinfos)-len(skiptests)} -- {len(report)/(len(vinfos)-len(skiptests))}")
    print(f"FRACTION SUPPORTED: {len(vinfos)-len(skiptests)}/{len(vinfos)}")

if __name__ == "__main__":
    vinfos = collect_validateinfo(root_manifest_file)
    execute_tests(vinfos)