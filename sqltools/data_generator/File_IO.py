import os
from typing import TextIO
from cli_utilities import UtilitiesInterface


class FileIO:
    """
    This class is meant as an abstract layer for a file.
    In this way multiple classes can share the same instance of the file.
    """

    __file_name: str
    __output_file: TextIO = None

    def __init__(self, output_file_name: str, overwrite: bool = False) -> None:
        """
        Constructor: opens the file for appending.
        """
        self.__file_name = output_file_name
        if not os.path.isfile(self.__file_name):
            UtilitiesInterface.create_dir_of_file(self.__file_name)
        if overwrite:
            self.__output_file = open(self.__file_name, 'w', encoding='utf-8')
        else:
            self.__output_file = open(self.__file_name, 'a', encoding='utf-8')

    def __del__(self) -> None:
        """
        Destructor: closes the file.
        :return: None
        """
        try:
            self.__output_file.close()
        except AttributeError:
            print("Output file of data generator was not opened.")

    def write(self, write_string: str) -> None:
        """
        This method writes write_string to the opened file.
        :type write_string: str
        :param write_string: The string that needs to be written to the file.
        :return: None
        """
        self.__output_file.write(write_string)
