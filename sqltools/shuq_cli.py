from rdflib import Graph
from slsparser.shapels import parse, SANode, Op
from slsparser.utilities import expand_shape, negation_normal_form
from shuq.unaryquery import translate_conformance_all

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("usage: shapefilename!")

    shapefile = sys.argv[1]

    shapesgraph = Graph()
    shapesgraph.parse(shapefile)

    definitions, targets = parse(shapesgraph)

    for key in definitions.keys():
        print(key)
        print(negation_normal_form(expand_shape(definitions, SANode(Op.NOT, [definitions[key]]))))

    conformance_sqlquery = translate_conformance_all(definitions, targets, target_all=False)

    print(conformance_sqlquery)