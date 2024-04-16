from converter import NqToTtl, TtlToCsv, CsvToDb, Mode
from cli_utilities import UtilitiesInterface


class Converter:  # Do not use this class directly, use ConverterInterface instead. (see converter_interface.py)

    __overwrite: bool
    __csv_files: list[str]
    __path_output_file: str
    __path_working_directory: str
    __path_input_file: str
    __no_database: bool
    __mode: Mode

    def __init__(self, path_input_file: str, path_working_directory: str, path_output_file: str,
                 mode: Mode, overwrite: bool = False):
        """
        Constructor
        :type path_input_file: str | Empty String for stdin
        :param path_input_file: The input file of type .ttl | .nq
        :type path_working_directory: str
        :param path_working_directory: The working directory to store the temporary files
        :type path_output_file: str
        :param path_output_file: The output file of type .db | .duckdb
        :type mode: Mode
        :param mode: The mode of the converter
        :type overwrite: bool
        :param overwrite: If the output file already exists, overwrite it
        :raise FileNotFoundError: If the input file does not exist
        :raise FileNotFoundError: If the working directory does not exist
        :raise TypeError: If path_input_file is not of type .ttl | .nq
        :raise TypeError: If path_output_file is not of type .db | .duckdb*
        :raise duckdb.IOException: If the database could not be created or opened
        :raise FileExistsError: If the path_output_file already exists and overwrite_files is False
        :raise NotADirectoryError: If path_working_directory is not a directory
        :raise PermissionError: If path_working_directory is not writable
        :raise FileExistsError: If path_working_directory already contains files and overwrite_files is False
        :raise TypeError: If overwrite is not of type bool
        :raise TypeError: If mode is not of type Mode
        *duckdb is a new file format that is similar to sqlite3
        :return: None
        """

        if mode not in Mode:
            raise TypeError(f"{mode} is not of type Mode")
        self.__mode = mode

        if type(overwrite) is not bool:
            raise TypeError(f"{overwrite} is not of type bool")
        self.__overwrite = overwrite

        if not path_working_directory.endswith('/'):
            path_working_directory = path_working_directory + '/'

        self.__no_database = not (mode == Mode.NQ_TO_DB or mode == Mode.TTL_TO_DB or mode == Mode.CSV_TO_DB)

        import os
        if path_input_file == '' or path_input_file == 'stdin':
            path_input_file = 'stdin'
        elif not os.path.isfile(path_input_file):
            raise FileNotFoundError(f"{path_input_file} does not exist")

        if not os.path.isdir(path_working_directory):
            os.makedirs(path_working_directory, exist_ok=True)

        if (not os.path.isfile(path_output_file) and not (
                self.__mode == Mode.NQ_TO_CSV or self.__mode == Mode.TTL_TO_CSV)):
            UtilitiesInterface.create_dir_of_file(path_output_file)

        if os.path.isfile(path_output_file) and not overwrite and not self.__no_database:
            UtilitiesInterface.create_dir_of_file(path_output_file)

        if (not path_output_file.endswith('.db') and not path_output_file.endswith('.duckdb') and
                not self.__no_database):
            raise TypeError(f"{path_output_file} is not of type .db or .duckdb")

        if (not (path_input_file.endswith('.ttl') or path_input_file == 'stdin') and
                (mode == Mode.TTL_TO_DB or mode == Mode.TTL_TO_CSV)):
            raise TypeError(f"{path_input_file} is not of type .ttl, this is required in this mode")

        if not path_input_file.endswith('.nq') and (mode == Mode.NQ_TO_TTL or mode == Mode.NQ_TO_DB or
                                                    mode == Mode.NQ_TO_CSV):
            raise TypeError(f"{path_input_file} is not of type .nq, this is required in this mode")

        self.__path_input_file = path_input_file
        self.__path_working_directory = path_working_directory
        self.__path_output_file = path_output_file
        self.__csv_files = self.__get_csv_file_names()

    def __get_csv_file_names(self) -> list[str]:
        """
        This function will return the names of the 6 .csv files
        :rtype: list[str]
        :return: A list of the names of the 6 .csv files
        """
        return [self.__path_working_directory + 'triples.csv',
                self.__path_working_directory + 'iris.csv',
                self.__path_working_directory + 'nodes.csv',
                self.__path_working_directory + 'blanks.csv',
                self.__path_working_directory + 'literals.csv',
                self.__path_working_directory + 'numerics.csv']

    def __convert_nq_to_ttl(self) -> None:
        """
        This function will convert the .nq file to a .ttl file and store it in the working directory
        :return: None
        :precondition: self.__path_input_file contains the path to the .nq file
        :precondition: self.__path_working_directory contains the path to the working directory
        :postcondition: self.__path_input_file contains the path to the .ttl file
        """
        if self.__mode == Mode.NQ_TO_TTL:
            output_file: str = self.__path_output_file
        else:
            output_file: str = self.__path_working_directory + 'temp.ttl'

        nq_to_ttl: NqToTtl = NqToTtl(self.__path_input_file, output_file, self.__overwrite)
        self.__path_input_file = output_file
        nq_to_ttl.run_converter()

    def __convert_ttl_to_csv(self, berkeley=False, berkeleydbpath=None) -> None:
        """
        This function will convert the .ttl file to multiple .csv files and store them in the working directory
        :return: None
        :precondition: self.__path_input_file contains the path to the .ttl file
        :precondition: self.__path_working_directory contains the path to the working directory
        :postcondition: self.__csv_files contains the path to the 6 .csv files
        """
        ttl_to_csv: TtlToCsv = TtlToCsv(self.__path_input_file, self.__path_working_directory, self.__overwrite)
        temp_files: list[str] = ttl_to_csv.run_converter(berkeley=berkeley, berkeleydbpath=berkeleydbpath)
        self.__csv_files = temp_files

    def __convert_csv_to_db(self) -> None:
        """
        This function will convert the .csv files to a .db file and store it in the working directory
        :return: None
        :raise duckdb.IOException: If the .db cannot be created or opened
        :precondition: self.__csv_files contains the path to the 6 .csv files
        :precondition: self.__path_output_file contains the path to the output file
        """
        csv_to_db: CsvToDb = CsvToDb(self.__csv_files, self.__path_output_file, self.__overwrite)
        csv_to_db.run_converter()

    def run_converter(self, berkeley=False, berkeleydbpath=None) -> None:
        """
        This function will convert the input file to the output file
        :return: None
        :raise duckdb.IOException: If the .db cannot be created or opened
        :precondition: self.__path_input_file contains the path to the input file
        :precondition: self.__path_output_file contains the path to the output file
        :postcondition: self.__path_output_file contains the path to the output file
        """
        if self.__mode == Mode.NQ_TO_TTL or self.__mode == Mode.NQ_TO_CSV or self.__mode == Mode.NQ_TO_DB:
            self.__convert_nq_to_ttl()
        if not (self.__mode == Mode.NQ_TO_TTL or self.__mode == Mode.CSV_TO_DB):
            self.__convert_ttl_to_csv(berkeley=berkeley, berkeleydbpath=berkeleydbpath)
        if not self.__no_database:
            self.__convert_csv_to_db()
