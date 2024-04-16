import sys
from typing import TextIO
from rdflib import Graph, URIRef, BNode, Literal, XSD, ConjunctiveGraph
from rdflib.store import NO_STORE, VALID_STORE


class TtlToCsv:
    __input: str
    __file_blanks: TextIO
    __file_iris: TextIO
    __file_literals: TextIO
    __file_nodes: TextIO
    __file_numerics: TextIO
    __file_triples: TextIO
    __IRIs: dict[URIRef, int]
    __Blanks: dict[BNode, int]
    __Literals: dict[Literal, int]
    __index: int

    @staticmethod
    def __check_file_existence(files: list[str], overwrite: bool) -> bool:
        """
        This function will check if the files exist
        :type files: list[str]
        :param files: The files to check
        :type overwrite: bool
        :param overwrite: If the files already exist, overwrite them
        :rtype: bool
        :return: True if the files exist, False otherwise
        """
        if overwrite:
            return False
        
        import os
        for file in files:
            if os.path.isfile(file):
                return True
        return False

    def __init__(self, input_file: str, output_directory: str, overwrite: bool = True):
        """
        Constructor
        :type input_file: str
        :param input_file: The input file of type .ttl
        :type output_directory: str
        :param output_directory: The output directory
        :type overwrite: bool
        :param overwrite: If the output file already exists, overwrite it
        :raise FileNotFoundError: If the input file does not exist
        :raise NotADirectoryError: If the output directory is not a directory
        :raise PermissionError: If the output directory is not writable
        :raise FileExistsError: If the output directory already contains files and overwrite is False
        :precondition: The output directory must exist
        """
        import os
        if not os.path.isdir(output_directory):
            os.makedirs(output_directory, exist_ok=True)

        if not os.access(output_directory, os.W_OK):
            raise PermissionError(f"{output_directory} is not writable")

        if output_directory.endswith('/'):
            output_directory = output_directory[:-1]

        if not os.path.isfile(input_file) and not input_file == 'stdin':
            raise FileNotFoundError(f"{input_file} does not exist")

        if self.__check_file_existence([f"{output_directory}/blanks.csv", f"{output_directory}/iris.csv",
                                        f"{output_directory}/literals.csv", f"{output_directory}/nodes.csv",
                                        f"{output_directory}/numerics.csv", f"{output_directory}/triples.csv"],
                                       overwrite):
            raise FileExistsError(f"{output_directory} already contains files")

        self.__input: str = input_file
        # Initiate Blanks
        self.__file_blanks = open(f"{output_directory}/blanks.csv", "w", encoding='utf-8')
        self.__file_blanks.write('Node, Alias\n')
        # Initiate IRIs
        self.__file_iris = open(f"{output_directory}/iris.csv", "w", encoding='utf-8')
        self.__file_iris.write('Node, Value\n')
        # Initiate Literals
        self.__file_literals = open(f"{output_directory}/literals.csv", "w", encoding='utf-8')
        self.__file_literals.write('Node, Value, Type, Lang\n')
        # Initiate Nodes
        self.__file_nodes = open(f"{output_directory}/nodes.csv", "w", encoding='utf-8')
        self.__file_nodes.write('Node\n')
        # Initiate Numerics
        self.__file_numerics = open(f"{output_directory}/numerics.csv", "w", encoding='utf-8')
        self.__file_numerics.write('Node, Value\n')
        # Initiate Triples
        self.__file_triples = open(f"{output_directory}/triples.csv", "w", encoding='utf-8')
        self.__file_triples.write('Subject, Predicate, Object\n')

        self.__IRIs = {}  # dict
        self.__Blanks = {}  # dict
        self.__Literals = {}  # dict
        self.__index = 0

    def __del__(self):
        """
        Destructor, this function will close all open files.
        :return: None
        """
        try:
            self.__file_triples.close()
        except AttributeError:
            print("Triples file was not opened.")
        try:
            self.__file_nodes.close()
        except AttributeError:
            print("Nodes file was not opened.")
        try:
            self.__file_iris.close()
        except AttributeError:
            print("IRIs file was not opened.")
        try:
            self.__file_literals.close()
        except AttributeError:
            print("Literals file was not opened.")
        try:
            self.__file_numerics.close()
        except AttributeError:
            print("Numerics file was not opened.")
        try:
            self.__file_blanks.close()
        except AttributeError:
            print("Blanks file was not opened.")

    @staticmethod
    def __is_digit(s: str) -> bool:
        """
        This function will check if a string is a digit.
        :type s: str
        :param s: The string to check
        :rtype: bool
        :return: True if the string is a digit, False otherwise
        """
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def __get_stdin_subject(s: str) -> URIRef | BNode:
        """
        This function will return the first parameter of a triple.
        :type s: str
        :param s: The string to check
        :rtype: URIRef | BNode
        :return: The first parameter of a triple
        """
        if s.startswith('<') and s.endswith('>'):
            return URIRef(s[1:-1])
        return BNode(s)

    @staticmethod
    def __get_stdin_predicate(p: str) -> URIRef:
        """
        This function will return the second parameter of a triple.
        :type p: str
        :param p: The string to check
        :rtype: URIRef
        :return: The second parameter of a triple
        """
        if p.startswith('<') and p.endswith('>'):
            return URIRef(p[1:-1])
        if p == "a":
            return URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        return URIRef(p)

    def __get_stdin_object(self, o: str) -> URIRef | BNode | Literal:
        """
        This function will return the third parameter of a triple.
        :type o: str
        :param o: The string to check
        :rtype: URIRef | BNode | Literal
        :return: The third parameter of a triple
        :raise ValueError: If the third parameter is not a URIRef, BNode or Literal
        """
        if o.startswith('<') and o.endswith('>'):
            return URIRef(o[1:-1])
        if o.startswith('"') and o.endswith('"'):
            return Literal(o[1:-1])
        if o.startswith('"') and not o.endswith('"') and o.__contains__('@'):
            return Literal(o.split('@')[0][1: -1], lang=o.split('@')[1])
        if o.startswith('_:'):
            return BNode(o[2:])
        if o == 'true' or o == 'false':
            return Literal(o, datatype="http://www.w3.org/2001/XMLSchema#boolean")
        if self.__is_digit(o):
            return Literal(o, datatype="http://www.w3.org/2001/XMLSchema#integer")
        if o.__contains__('e') or o.__contains__('E'):
            return Literal(o, datatype="http://www.w3.org/2001/XMLSchema#double")
        if o.__contains__('.'):
            return Literal(o, datatype="http://www.w3.org/2001/XMLSchema#decimal")
        raise ValueError(f"Invalid value {o}")

    def __add_line_to_graph(self, g: Graph, line: str) -> Graph:
        """
        This function will add a line to a graph.
        :type g: Graph
        :param g: The graph to add the line to
        :type line: str
        :param line: The line to add to the graph.
        :rtype: Graph
        :return: The graph with the line added to it
        """
        temp: list[str] = line.split(' ')
        if temp[0] == '@prefix':
            print(f"Error: {temp}")
            print("Prefixes are not supported with stdin")
            return g
        if len(temp) != 4:
            print(f"Error: {temp}")
            print(f"Length: {len(temp)} should be 3 and a . with a space in between each")
            return g
        try:
            stdin_subject: URIRef | BNode = self.__get_stdin_subject(temp[0])
            stdin_predicate: URIRef = self.__get_stdin_predicate(temp[1])
            stdin_object: URIRef | BNode | Literal = self.__get_stdin_object(temp[2])
            g.add((stdin_subject, stdin_predicate, stdin_object))
        except ValueError:
            print("Error: " + temp[2])
            print("Abbreviations are not supported with stdin")
            return g
        return g

    def __handle_pipe(self, g: Graph) -> Graph:
        """
        This function will handle the pipe input.
        :type g: Graph
        :param g: The graph to add the triples to
        :rtype: Graph
        :return: The graph with the added triples
        """
        for line in sys.stdin:
            g = self.__add_line_to_graph(g, line)
        return g

    def __handle_stdin(self, g: Graph) -> Graph:
        """
        This function will handle the stdin input.
        :type g: Graph
        :param g: The graph to add the triples to
        :rtype: Graph
        :return: The graph with the added triples
        """
        if not sys.stdin.isatty():  # Check if input is piped.
            return self.__handle_pipe(g)
        temp_input: str = ' '
        print("Please enter your triples (EOF to end):")
        while not (temp_input == 'EOF'):
            temp_input = input()
            self.__add_line_to_graph(g, temp_input)
        return g

    def __build_mem(self) -> Graph:
        """
        This function will build the .ttl file as a graph in memory.
        :rtype: Graph
        :return: The graph
        """
        g: Graph = Graph()
        if not self.__input == 'stdin':
            g.parse(self.__input, format='ttl')  # TODO if enough time, add support for other formats
            return g
        return self.__handle_stdin(g)

    def __handle_iris(self, n: URIRef) -> int:
        """
        This function will add the IRIs to the files.
        :type n: URIRef
        :param n: An IRI
        :rtype: int
        :return: The id of the IRI
        """
        if n in self.__IRIs:  # IRI already stored
            return self.__IRIs[n]
        my_node: int = self.__index
        self.__index += 1
        self.__file_nodes.write(f"{my_node}\n")
        self.__IRIs[n] = my_node
        self.__file_iris.write(f"{my_node},{str(n)}\n")
        return my_node

    def __handle_b_node(self, n: BNode) -> int:
        """
        This function will add the blank node to the files.
        :type n: BNode
        :param n: A blank node
        :rtype: int
        :return: The id of the Blank node
        """
        if n in self.__Blanks:  # Blank node already stored
            return self.__Blanks[n]
        my_node: int = self.__index
        self.__index += 1
        self.__file_nodes.write(f"{my_node}\n")
        self.__Blanks[n] = my_node
        self.__file_blanks.write(f"{my_node},{str(n)}\n")
        return my_node

    def __handle_literal(self, o: Literal) -> int:
        """
        This function will add the literal to the files.
        :type o: Literal
        :param o: A Literal
        :rtype: int
        :return: The id of the Literal
        """
        if o in self.__Literals:  # Literal already stored
            return self.__Literals[o]
        my_obj: int = self.__index
        self.__index += 1
        self.__file_nodes.write(f"{my_obj}\n")
        datatype: str = str(o.datatype) if o.datatype is not None else XSD.string
        language: str = 'NULL'
        if o.language is not None:  # Literal is a String with language tag
            datatype = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#langString'
            language = o.language
        elif o.datatype in [XSD.integer, XSD.double, XSD.decimal]:  # Literal is an integer
            try: # try to add to numerics, if not possible, skip
                numeric_o = float(o)
                self.__file_numerics.write(f"{my_obj},{numeric_o}\n")
            except Exception as e:
                print(f"CONVERTER ERROR: {e}")
                pass
        # Not correct: when no type is defined, we do not know what it is!
        # elif o.datatype is None:  # Literal is a String without language tag, or quoted value.
        #     datatype = 'http://www.w3.org/2001/XMLSchema#string'
        self.__Literals[o] = my_obj
        new_object: str = str(o).replace('"', '""')
        self.__file_literals.write(f"{my_obj},\"{new_object}\",{datatype},{language}\n")
        return my_obj

    def __add_triples(self, g: Graph) -> None:
        """
        This function will add the triples from g to the memory
        :type g: Graph
        :param g: A data shape
        :return: None
        """
        for (s, p, o) in g:
            my_obj: int = -1
            my_sub: int = -1
            if isinstance(o, URIRef):
                my_obj = self.__handle_iris(o)
            elif isinstance(o, BNode):
                my_obj = self.__handle_b_node(o)
            elif isinstance(o, Literal):
                my_obj = self.__handle_literal(o)
            if isinstance(s, URIRef):
                my_sub = self.__handle_iris(s)
            elif isinstance(s, BNode):
                my_sub = self.__handle_b_node(s)
            self.__file_triples.write(f"{my_sub},{str(p)},{my_obj}\n")

    def run_converter(self, berkeley=False, berkeleydbpath=None) -> list[str]:
        """
        This function will convert the .ttl file in multiple .csv files
        :return: A list of all the output files
        :rtype: list[str]
        """
        #ADDED: added berkeley option
        if not berkeley: # Other's implementation
            #print(f"Start loading .ttl file: {self.__input}")
            g: Graph = self.__build_mem()
            #print(f"Finished loading .ttl file: {self.__input}")
            #print("Start building .csv files")
            self.__add_triples(g)
            #print("Finished building .csv files")
            return self.__get_output_files()
        
        if berkeleydbpath is None:
            import tempfile
            berkeleydbpath = tempfile.NamedTemporaryFile().name

        datagraph = ConjunctiveGraph("BerkeleyDB")
        rt = datagraph.open(berkeleydbpath, create=False)

        print("LOADING BERKELEY DATAGRAPH...")
        if rt == NO_STORE:
            # There is no underlying BerkeleyDB infrastructure, so create it
            print("CONV Creating new BerkeleyDB")
            datagraph.open(berkeleydbpath, create=True)
            datagraph.parse(self.__input)
            datagraph.commit()
            print(f"CONV Triples in data graph: {len(datagraph)}")
        else:
            print("CONV Using existing BerkeleyDB")
            assert rt == VALID_STORE, "CONV The underlying BerkeleyDB store is corrupt"

        print(f"CONV Triples still in data graph: {len(datagraph)}")
        self.__add_triples(datagraph)

        datagraph.close()
        return self.__get_output_files()

            


    def __get_output_files(self) -> list[str]:
        """
        This function will return a list of all the output files
        :rtype: list[str]
        :return: A list of all the output files
        """
        output_files: list[str] = [self.__file_triples.name, self.__file_iris.name, self.__file_nodes.name,
                                   self.__file_blanks.name, self.__file_literals.name, self.__file_numerics.name]
        return output_files


def run() -> None:
    """
    This function will run a test
    :return: None
    """
    input_ttl_file: str = "../ttl_data/input.ttl"
    output_directory: str = "../output/csv/"
    print(TtlToCsv(input_ttl_file, output_directory).run_converter())


if __name__ == '__main__':
    run()
