# Pseudo code database

## How to use the database package
To make it easier to use the package, there is an interface available.
The interface is everything you need to get complete use of the package.
The interface has 1 function. This function is execute; it will execute the SQL statement on the database.

## how to import the package
Use the import statement: __from database import DatabaseInterface__

## How to use the interface
The interface only consists out of non-static methods, so you do need to create an instance of the interface.
You can just use __Database = DatabaseInterface(database_file_name)__  
Later you can call __Database.execute(SQL_query)__.

### DatabaseInterface
DatabaseInterface(database_file_name):  
&emsp;self.__database = RunDB(database_file_name)

execute(SQL_query):  
&emsp;return __database.execute(self, SQL_query)

### RunDB
RunDB(database_file_name, readonly = True):  
&emsp;self.__database_file_name = database_file_name  
➡ &emsp;self.__database = try to make database hot.

execute(self, SQL_query):  
&emsp;return self.__database.execute(SQL_query).fetchall()
