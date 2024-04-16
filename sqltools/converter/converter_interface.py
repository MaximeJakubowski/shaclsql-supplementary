from converter import Converter, Mode


class ConverterInterface:

    @staticmethod
    def run_converter(path_input_file: str, path_working_directory: str, path_output_file: str,
                      mode: Mode, overwrite_db: bool = False, berkeley=False, berkeleydbpath=None) -> None:
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
        :type overwrite_db: bool
        :param overwrite_db: If the output file already exists, overwrite it
        :raise FileNotFoundError: If the input file does not exist
        :raise FileNotFoundError: If the working directory does not exist
        :raise TypeError: If path_input_file is not of type .ttl | .nq
        :raise TypeError: If path_output_file is not of type .db | .duckdb*
        :raise duckdb.IOException: If the database could not be created or opened
        :raise FileExistsError: If the path_output_file already exists and overwrite_files is False
        :raise NotADirectoryError: If path_working_directory is not a directory
        :raise PermissionError: If path_working_directory is not writable
        :raise FileExistsError: If path_working_directory already contains files and overwrite_files is False
        :raise TypeError: If overwrite_db is not of type bool
        :raise TypeError: If mode is not of type Mode
        *duckdb is a new file format that is similar to sqlite3
        :return: None
        """
        if not overwrite_db:
            Converter(path_input_file, path_working_directory, path_output_file, mode)\
                .run_converter(berkeley=berkeley, berkeleydbpath=berkeleydbpath)
            return
        Converter(path_input_file, path_working_directory, path_output_file, mode,
                  overwrite_db)\
                    .run_converter(berkeley=berkeley, berkeleydbpath=berkeleydbpath)
