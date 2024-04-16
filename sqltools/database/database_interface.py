from database import RunDB


class DatabaseInterface:

    __database: RunDB

    def __init__(self, database_file_name: str, read_only: bool = True):
        """
        Constructor
        :type database_file_name: str
        :param database_file_name: The file name
        :type read_only: bool
        :param read_only: If the database should be read only (True by default)
        """
        self.__database = RunDB(database_file_name, read_only)

    def execute(self, SQL_query: str) -> list[tuple]:
        """
        This function will execute the query
        :type SQL_query: str
        :param SQL_query: The SQL query
        :rtype: list[tuple]
        :return: : A list of rows
        :raise IOError: If the query could not be executed
        """
        return self.__database.execute(SQL_query)
