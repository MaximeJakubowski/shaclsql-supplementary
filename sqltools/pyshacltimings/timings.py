import os
from time import time
from typing import TextIO
from rdflib import Graph
from pyshacl import validate


class Validator:

    __output_file: str
    __input_shapes_files: list[str]
    __data_graph: Graph
    __overwrite: bool

    def __init__(self, input_data_file: str, input_shapes_files: list[str], output_file: str, overwrite: bool = False):
        """
        Constructor
        :type input_data_file: str
        :param input_data_file: The path to the input data file.
        :type input_shapes_files: list[str]
        :param input_shapes_files: The paths to the input shapes files.
        :type output_file: str
        :param output_file: The path to the output file.
        :type overwrite: bool
        :param overwrite: If the output file already exists, overwrite it.
        """
        if not os.path.isfile(input_data_file):
            raise FileNotFoundError(f"File not found: {input_data_file}")
        for input_shapes_file in input_shapes_files:
            if not os.path.isfile(input_shapes_file):
                raise FileNotFoundError(f"File not found: {input_shapes_file}")
        if not os.path.isdir(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

        self.__data_graph = Graph()
        self.__data_graph.parse(input_data_file, format='ttl')
        self.__input_shapes_files = input_shapes_files
        self.__output_file = output_file
        self.__overwrite = overwrite

    def __write_outputfile(self, output_file: TextIO) -> None:
        """
        This method will write the output file.
        :type output_file: TextIO
        :param output_file: The output file.
        :return: None
        """
        output_file.write("\"file\",\"timing 1\",\"timing 2\",\"timing 3\"\n")
        for input_shapes_file in self.__input_shapes_files:
            print(f"Validating {input_shapes_file}")
            g = Graph()
            g.parse(input_shapes_file, format='ttl')
            output_file.write(f"\"{input_shapes_file}\"")
            for i in range(3):
                output_file.write(f",\"{str(self.time_validate(self.__data_graph, g))}\"")
            output_file.write("\n")

    def execute(self) -> None:
        """
        This method will execute the validator.
        :return: None
        """
        if self.__overwrite or not os.path.isfile(self.__output_file):
            with open(self.__output_file, "w", encoding='utf-8') as output_file:
                self.__write_outputfile(output_file)

    @staticmethod
    def time_validate(data_graph: Graph, shacl_graph: Graph) -> int:
        """
        ADDED:
        this function returns validation time in miliseconds
        """
        start_time = int(time() * 1000)
        conforms, results_graph, results_text = validate(data_graph,
                 shacl_graph=shacl_graph,
                 ont_graph=None,
                 inference=None,
                 abort_on_first=False,
                 allow_infos=True,
                 allow_warnings=True,
                 meta_shacl=False,
                 advanced=False,
                 js=False,
                 debug=False)
        print(f"CONFORMS {conforms}")
        end_time = int(time() * 1000)
        return end_time - start_time


def run() -> None:
    """
    This method runs the validator program.
    :return: None
    """
    input_data_file = './ttl_data/temp.ttl'
    input_shapes_file = './benchmark_shapes/airportshape.ttl'
    output_file = './output/results.csv'
    Validator(input_data_file, [input_shapes_file], output_file, True)


if __name__ == '__main__':
    run()
