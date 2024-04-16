import os
from timings import Validator


class Main:
    __path_input_files: list[str]
    __path_output_file: str
    __path_data_file: str
    __overwrite: bool

    def __init__(self):
        """
        Constructor
        """
        self.__path_input_files = []
        self.__path_output_file = './output/results.csv'
        self.__path_data_file = './ttl_data/temp.ttl'
        self.__overwrite = False

    @staticmethod
    def __print_help() -> None:
        """
        This function will print the help message.
        :return: None
        """
        print("This script will run the timings for the given input data file and shape files.")
        print("Usage: main.py -i <input_files> -e -o <output_file> -d <data_file> -w")
        print("")
        print("-i or --input or --input-files is the paths to the input shapes graph files")
        print("The paths to the input files should be separated by a space, if there are spaces in the path use quotes")
        print("The input data files must be of type .ttl")
        print("It is required to close this tag with -e or --end-input")
        print("If there is a flag -a or --all before the -e or --end-input, "
              "a list of predefined shape files will be used.")
        print("")
        print("-o or --output is the path to the output file")
        print("-o or --output is optional, if not provided ./output/result.csv will be used")
        print("The output file must be of type .csv")
        print("The directory where the output file is located must exist")
        print("")
        print("-d or --data is the path to the data file")
        print("The database file must be of type .ttl")
        print("")
        print("-e or --end-input is required when the flag -i or --input or --input-files is present")
        print("-e or --end-input will end the input files")
        print("If there is no end flag present, the script will read all the arguments until the end of the arguments")
        print("Other flags will be read as arguments of the previous flag")
        print("The end flag is not required if the last flag is -i or --input or --input-files")
        print("")
        print("-w or --overwrite is optional")
        print("-w or --overwrite will overwrite the output file if it already exists")
        print("")
        print("-h or --help is optional")
        print("-h or --help will print this help message")

    @staticmethod
    def __get_all() -> list[str]:
        """
        This function will return a list of all files in a default directory
        :rtype: list[str]
        :return: A list of all files in a default directory
        """
        os.makedirs("./benchmark_shapes/", exist_ok=True)
        file_list: list[str] = os.listdir("./benchmark_shapes/")
        for i in range(len(file_list)):
            file_list[i] = "./benchmark_shapes/" + file_list[i]
        return file_list

    @staticmethod
    def __filter_end_input(shapes: list[str]) -> list[str]:
        """
        This method filters the files that need to be validated.
        :type shapes: list[str]
        :param shapes: The files that need to be validated.
        :rtype: list[str]
        :return: The filtered files.
        """
        list_shapes = []
        for shape in shapes:
            if shape == "-e" or shape == "--end-input":
                return list_shapes
            if shape == "-a" or shape == "--all":
                return Main.__get_all()
            list_shapes.append(shape)
        return list_shapes

    def run(self) -> None:
        """
        This method runs the timings program.
        :return: None
        """
        import sys

        for i in range(1, len(sys.argv)):
            if sys.argv[i] == "-h" or sys.argv[i] == "--help":
                Main.__print_help()
                sys.exit(0)
            if sys.argv[i] == "-w" or sys.argv[i] == "--overwrite":
                self.__overwrite = True
            if sys.argv[i - 1] == "-i" or sys.argv[i - 1] == "--input" or sys.argv[i - 1] == "--input-files":
                self.__path_input_files = Main.__filter_end_input(sys.argv[i:])
            if sys.argv[i - 1] == "-o" or sys.argv[i - 1] == "--output":
                self.__path_output_file = sys.argv[i]
            if sys.argv[i - 1] == "-d" or sys.argv[i - 1] == "--data":
                self.__path_data_file = sys.argv[i]
        try:
            Validator(self.__path_data_file, self.__path_input_files, self.__path_output_file,
                      self.__overwrite).execute()
            print("Executed successfully")
        except Exception as msg:
            print(msg)
            sys.exit(1)


if __name__ == '__main__':
    Main().run()
