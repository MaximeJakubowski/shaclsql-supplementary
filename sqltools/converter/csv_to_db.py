import duckdb
from duckdb import DuckDBPyConnection
from cli_utilities import UtilitiesInterface


class CsvToDb:

    __input: list[str]
    __output: str

    def __init__(self, input_files: list[str], output_file: str, overwrite: bool = True):
        """
        Constructor
        :type input_files: list[str]
        :param input_files: A list of input files of type .csv
        :type output_file: str
        :param output_file:The output file of type .db | .duckdb
        :type overwrite: bool
        :param overwrite: If the output file already exists, overwrite it
        :pre: input_files contains 6 .csv files in the following order: Triples, IRIs, Nodes, Blanks, Literals, Numerics
        :pre: output_file is of type .db | .duckdb
        :raise ValueError: If the input_files list does not contain 6 files
        :raise ValueError: If the output_file is not of type .db | .duckdb
        :raise ValueError: If the input_files are not of type .csv
        :raise FileNotFoundError: If one of the input_files does not exist
        :raise FileExistsError: If the output_file already exists and overwrite is False
        """
        if len(input_files) != 6:
            raise ValueError("The input files must contain 6 files")
        i: int
        for i in range(0, len(input_files)):
            if input_files[i].split('.')[-1] != 'csv':
                raise ValueError(f"The input file at index {i} must be of type .csv")
        if output_file.split('.')[-1] != 'db' and output_file.split('.')[-1] != 'duckdb':
            raise ValueError("The output file must be of type .db or .duckdb")

        import os
        for input_file in input_files:
            if not os.path.isfile(input_file):
                raise FileNotFoundError(f"{input_file} does not exist")

        if os.path.isfile(output_file) and not overwrite:
            raise FileExistsError(f"{output_file} already exists")
        UtilitiesInterface.create_dir_of_file(output_file)

        self.__input = input_files
        self.__output = output_file

    def __add_triples(self, db: duckdb.DuckDBPyConnection) -> None:
        """
        This function will add the Triples to the database
        :type db: duckdb.DuckDBPyConnection
        :param db: The database
        :return: None
        """
        #print(f"Start loading: {self.__input[0]}")
        db.execute(f"CREATE TABLE IF NOT EXISTS Triples(Subject INTEGER, Predicate VARCHAR, Object INTEGER);")
        db.execute("DELETE FROM Triples WHERE True;")
        db.execute(f"COPY Triples FROM '{self.__input[0]}' WITH (HEADER 1, DELIMITER ',');")
        #print(f"Finished loading: {self.__input[0]}")

    def __add_iris(self, db: duckdb.DuckDBPyConnection) -> None:
        """
        This function will add the IRIs to the database
        :type db: duckdb.DuckDBPyConnection
        :param db: The database
        :return: None
        """
        #print(f"Start loading: {self.__input[1]}")
        db.execute(f"CREATE TABLE IF NOT EXISTS IRIs(Node INTEGER, Value VARCHAR);")
        db.execute("DELETE FROM IRIs WHERE True;")
        db.execute(f"COPY IRIs FROM '{self.__input[1]}' WITH (HEADER 1, DELIMITER ',');")
        #print(f"Finished loading: {self.__input[1]}")

    def __add_nodes(self, db: duckdb.DuckDBPyConnection) -> None:
        """
        This function will add the Nodes to the database
        :type db: duckdb.DuckDBPyConnection
        :param db: The database
        :return: None
        """
        #print(f"Start loading: {self.__input[2]}")
        db.execute(f"CREATE TABLE IF NOT EXISTS Nodes(Node INTEGER);")
        db.execute("DELETE FROM Nodes WHERE True;")
        db.execute(f"COPY Nodes FROM '{self.__input[2]}' WITH (HEADER 1, DELIMITER ',');")
        #print(f"Finished loading: {self.__input[2]}")

    def __add_blanks(self, db: duckdb.DuckDBPyConnection) -> None:
        """
        This function will add the Blanks to the database
        :type db: duckdb.DuckDBPyConnection
        :param db: The database
        :return: None
        """
        #print(f"Start loading: {self.__input[3]}")
        db.execute(f"CREATE TABLE IF NOT EXISTS Blanks(Node INTEGER, Alias VARCHAR);")
        db.execute("DELETE FROM Blanks WHERE True;")
        db.execute(f"COPY Blanks FROM '{self.__input[3]}' WITH (HEADER 1, DELIMITER ',');")
        #print(f"Finished loading: {self.__input[3]}")

    def __add_literals(self, db: duckdb.DuckDBPyConnection) -> None:
        """
        This function will add the Literals to the database
        :type db: duckdb.DuckDBPyConnection
        :param db: The database
        :return: None
        """
        #print(f"Start loading: {self.__input[4]}")
        db.execute(f"CREATE TABLE IF NOT EXISTS Literals(Node INTEGER, Value VARCHAR, Type VARCHAR, Lang VARCHAR);")
        db.execute("DELETE FROM Literals WHERE True;")
        db.execute(f"COPY Literals FROM '{self.__input[4]}' WITH (HEADER 1, DELIMITER ',', NULLSTR 'NULL');")
        #print(f"Finished loading: {self.__input[4]}")

    def __add_numerics(self, db: duckdb.DuckDBPyConnection) -> None:
        """
        This function will add the Numerics to the database
        :type db: duckdb.DuckDBPyConnection
        :param db: The database
        :return: None
        """
        #print(f"Start loading: {self.__input[5]}")
        db.execute(f"CREATE TABLE IF NOT EXISTS Numerics(Node INTEGER, VALUE DOUBLE);")
        db.execute("DELETE FROM Numerics WHERE True;")
        db.execute(f"COPY Numerics FROM '{self.__input[5]}' WITH (HEADER 1, DELIMITER ',');")
        #print(f"Finished loading: {self.__input[5]}")

    def run_converter(self) -> None:
        """
        This function will add the csv files to the database.
        :return: None
        :raise duckdb.IOException: If the database could not be created or opened
        :precondition: The input files must be of type .csv
        :precondition: The output file must be of type .db or .duckdb
        :precondition: The input files must exist
        :postcondition: The database will be created
        """
        #print("Start converting .csv files to .db file")
        msg: Exception
        try:
            db: DuckDBPyConnection = duckdb.connect(database=self.__output, read_only=False)
        except duckdb.IOException as msg:
            #print("Converting .csv files to .db file failed:")
            #print(msg)
            raise duckdb.IOException(msg)
        self.__add_triples(db)
        self.__add_iris(db)
        self.__add_nodes(db)
        self.__add_blanks(db)
        self.__add_literals(db)
        self.__add_numerics(db)
        db.close()
        #print("Finished converting .csv files to .db file")


def run() -> None:
    """
    This function will run a test
    :return: None
    """
    input_csv_file: list[str] = ["../output/csv/triples.csv", "../output/csv/iris.csv", "../output/csv/nodes.csv",
                                 "../output/csv/blanks.csv", "../output/csv/literals.csv", "../output/csv/numerics.csv"]
    output_db_file: str = "../db/rdf.duckdb"
    CsvToDb(input_csv_file, output_db_file).run_converter()


if __name__ == '__main__':
    run()
