from typing import TextIO
from cli_utilities import UtilitiesInterface


class NqToTtl:

    __input: str
    __output: str

    def __init__(self, input_file: str, output_file: str, overwrite: bool = True):
        """
        Constructor
        :type input_file: str
        :param input_file: The input file of type .nq
        :type output_file: str
        :param output_file: The output file of type .ttl
        :type overwrite: bool
        :param overwrite: If the output file already exists, overwrite it
        :raise FileNotFoundError: If the input file does not exist
        :raise TypeError: If the input file is not of type .nq
        :raise TypeError: If the output file is not of type .ttl
        :raise FileExistsError: If the output_file already exists and overwrite is False
        :return: None
        """
        import os
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"{input_file} does not exist")

        if not input_file.endswith('.nq'):
            raise TypeError(f"{input_file} is not of type .nq")

        if not output_file.endswith('.ttl'):
            raise TypeError(f"{output_file} is not of type .ttl")

        if os.path.isfile(output_file) and not overwrite:
            raise FileExistsError(f"{output_file} already exists")
        UtilitiesInterface.create_dir_of_file(output_file)

        self.__input = input_file
        self.__output = output_file

    @staticmethod
    def __convert_line(line: str) -> str:
        """
        This function will convert the line from .nq format to .ttl format
        :type line: str
        :param line:A line in .nq format
        :rtype: str
        :return: A line in .ttl format
        """
        split_line: list[str] = line.split()
        return_str: str = ''
        i: int
        for i in range(1, len(split_line)):
            if i == len(split_line) - 1:
                return_str = return_str + ' ' + split_line[i] + '\n'
            else:
                return_str = return_str + ' ' + split_line[i-1]
        return return_str

    def run_converter(self) -> None:
        """
        This function will convert the .ttl file in multiple .csv files
        :return: None
        """
        input_file: TextIO
        with open(self.__input, 'r', encoding='utf-8') as input_file:
            output_file: TextIO
            with open(self.__output, 'w', encoding='utf-8') as output_file:
                line: str
                for line in input_file:
                    converted_line: str = NqToTtl.__convert_line(line)
                    output_file.write(converted_line)


def run() -> None:
    """
    This function will run a test
    :return: None
    """
    input_ttl_file: str = "../nq_data/graphC.nq"
    output_csv_file: str = "../ttl_data/temp.ttl"
    NqToTtl(input_ttl_file, output_csv_file).run_converter()


if __name__ == '__main__':
    run()
