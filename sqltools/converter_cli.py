
from converter import ConverterInterface, Mode


class ConverterCLI:

    @staticmethod
    def __print_help() -> None:
        """
        This method prints the help message.
        :return: None
        """
        print("Usage: converter_cli.py -m <execution_mode> -i <input_file> -d <working_directory> -o <output_file> "
              "-w")
        print("")
        print("-m or --mode is the execution mode")
        print("-m or --mode is optional, if not provided ttl-to-csv will be used")
        print("The execution mode must be one of the following:")
        print("nq-to-ttl, nq-to-csv, nq-to-db, ttl-to-csv, ttl-to-db, csv-to-db")
        print("")
        print("-i or --input is the path to the input file")
        print("-i or --input is optional, if not provided stdin will be used")
        print("The input file must be of type .ttl or .nq")
        print("stdin is not supported for .nq data format")
        print("If the execution mode is nq-to-ttl, nq-to-csv or nq-to-db, the input file must be of type .nq")
        print("If the execution mode is ttl-to-csv or ttl-to-db, the input file must be of type .ttl")
        print("If the execution mode is csv-to-db, this argument is ignored")
        print("")
        print("-d or --directory is the path to the working directory")
        print("-d or --directory is optional, if not provided ../csv/output/ will be used")
        print("The working directory must exist")
        print("The working directory must be writable")
        print("")
        print("-o or --output is the path to the output file")
        print("-o or --output is optional, if not provided ../db/output.duckdb will be used")
        print("The output file must be of type .db or .duckdb")
        print("The output file must not exist or overwrite must be set to true")
        print("If the execution mode is nq-to-ttl, nq-to-csv or ttl-to-csv, this argument is ignored")
        print("")
        print("-w or --overwrite is optional")
        print("-w or --overwrite will overwrite the output file if it already exists")
        print("")
        print("-h or --help will display this message")
        print("For the API use converter_interface.py")

    @staticmethod
    def run() -> None:
        """
        This method runs the converter program.
        :return: None
        """
        import sys
        path_input_file: str = ''
        path_working_directory: str = './output/csv/'
        path_output_file: str = './output/db/output.duckdb'
        overwrite: bool = False
        mode: Mode = Mode.TTL_TO_CSV

        for i in range(1, len(sys.argv)):  # never use sys.argv[0] because it is the name of the file
            if sys.argv[i - 1] == '-m' or sys.argv[i - 1] == '--mode':
                if sys.argv[i] == 'csv-to-db':
                    mode = Mode.CSV_TO_DB
                elif sys.argv[i] == 'ttl-to-db':
                    mode = Mode.TTL_TO_DB
                elif sys.argv[i] == 'ttl-to-csv':
                    mode = Mode.TTL_TO_CSV
                elif sys.argv[i] == 'nq-to-db':
                    mode = Mode.NQ_TO_DB
                elif sys.argv[i] == 'nq-to-csv':
                    mode = Mode.NQ_TO_CSV
                elif sys.argv[i] == 'nq-to-ttl':
                    mode = Mode.NQ_TO_TTL
            elif sys.argv[i - 1] == '-i' or sys.argv[i - 1] == '--input':
                path_input_file = sys.argv[i]
            elif sys.argv[i - 1] == '-d' or sys.argv[i - 1] == '--directory':
                path_working_directory = sys.argv[i]
            elif sys.argv[i - 1] == '-o' or sys.argv[i - 1] == '--output':
                path_output_file = sys.argv[i]
            if sys.argv[i] == '-w' or sys.argv[i] == '--overwrite':
                overwrite = True
            if sys.argv[i] == '-h' or sys.argv[i] == '--help':
                ConverterCLI.__print_help()
                sys.exit(0)
        try:
            ConverterInterface().run_converter(path_input_file, path_working_directory, path_output_file, mode,
                                               overwrite)
            print("Executed successfully")
        except Exception as msg:
            print(msg)
            sys.exit(1)


if __name__ == '__main__':
    ConverterCLI.run()
