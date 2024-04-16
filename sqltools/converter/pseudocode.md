# Pseudo code converter

## How to use the converter package
To make it easier to use the package, there is an interface available.
The interface is everything you need to get complete use of the package.
The interface has 1 function. This function is execute; it will convert the file to the corresponding output.

## how to import the package
Use the import statement: __from converter import ConverterInterface, Mode__

## How to use the interface
The interface only consists out of static methods, so you don't need to create an instance of the interface.
You can just use 
__ConverterInterface.run_converter(path_input_file, path_working_directory, path_output_file, mode, overwrite_db)__
overwite_files is optional.

### ConverterInterface
if overwrite_files is None:  
&emsp;Converter(path_input_file, path_working_directory, path_output_file).run_converter()  
&emsp;return  
Converter(path_input_file, path_working_directory, path_output_file, overwrite_files).run_converter()

### Converter
Converter(path_input_file, path_working_directory, path_output_file, mode, overwrite = False):  
&emsp;self.__path_input_file = path_input_file  
&emsp;self.__path_working_directory = path_working_directory  
&emsp;self.__path_output_file = path_output_file  
&emsp;self.__mode = mode  
&emsp;self.__overwrite = overwrite

run_converter():  
➡ Check mode.  
&emsp;➡ Depending on mode:  
&emsp;&emsp;➡ Convert .nq to .ttl  
&emsp;&emsp;➡ Convert .ttl to 6 .csv files  
&emsp;&emsp;➡ Convert .csv files to .db/.duckdb file:  
Depending on the mode, the converter can start and stop at each step.

### nq_to_ttl
nq_to_ttl(path_input_file, path_output_file, overwrite = True):  
&emsp;self.__input = input_file  
&emsp;self.__output = output_file

run_converter():  
➡ Converts the .nq file to a .ttl file.

### ttl_to_csv
ttl_to_csv(files, overwrite = True):  
➡ Open the files.  
➡ Create dictionaries to store temp data.

run_converter():  
➡ Load the .ttl file.  
➡ Convert the .ttl file to 6 .csv files.

### csv_to_db
csv_to_db(input_files, output_file, overwrite = True):  
&emsp;self.__input = input_files  
&emsp;self.__output = output_file

run_converter():  
➡ Create a connection to the database.  
➡ Clear the database.  
➡ Create the tables & insert the data. (one by one)
