import os

import duckdb
from duckdb import DuckDBPyConnection
from cli_utilities import UtilitiesInterface


class RunDB:  # Do not import this class directly, use DatabaseInterface instead. (see database_interface.py)

    __database_file_name: str
    __db: DuckDBPyConnection

    def __init__(self, database_file_name: str, read_only: bool = True):
        """
        Constructor
        :type database_file_name: str
        :param database_file_name: The file name
        :type read_only: bool
        :param read_only: If the database should be read only (True by default)
        """
        self.__database_file_name = database_file_name
        msg: Exception  # Invalid Error: Failed to prepare query "SELECT "Predicate", "Subject" FROM "Triples" WHERE
        # ROWID BETWEEN 0 AND 122879": database is locked
        # Invalid Error: database is locked
        try:
            if not os.path.isfile:
                UtilitiesInterface.create_dir_of_file(self.__database_file_name)
            self.__db: DuckDBPyConnection = duckdb.connect(database=self.__database_file_name, read_only=read_only)
        except duckdb.IOException as msg:
            print(msg)

    def __del__(self):
        """
        Destructor
        """
        try:
            self.__db.close()
        except AttributeError:  # Database was not opened
            print("Database was not opened.")

    def execute(self, SQL_query: str) -> list[tuple]:
        """
        This function will execute the query
        :type SQL_query: str
        :param SQL_query: The SQL query
        :rtype: list[tuple]
        :return: : A list of rows
        :raise IOError: If the query could not be executed
        """
        try:
            result: list = self.__db.sql(SQL_query).fetchall()
        except duckdb.IOException as msg:
            print(msg)
            raise IOError(msg)
        return result

    @staticmethod
    def print_results(results: list[tuple]) -> None:
        """
        This function will print the results
        :type results: list[tuple]
        :param results: A list of rows
        :return: None
        """
        row: tuple
        for row in results:
            print(row)


def run():
    """
    This function will run a test
    :return: None
    """
    print("Hello World!")
    results: list[tuple] = RunDB('../db/output.duckdb').execute("SELECT * FROM Literals WHERE Lang is NULL")
    RunDB.print_results(results)
    print("Goodbye World!")


if __name__ == '__main__':
    run()
