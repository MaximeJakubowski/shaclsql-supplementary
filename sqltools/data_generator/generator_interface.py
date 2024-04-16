from data_generator import Generator


class GeneratorInterface:

    __generator: Generator

    def __init__(self, output_file_name: str, overwrite: bool = False):
        """
        Constructor
        :type output_file_name: str
        :param output_file_name: The name of the output file
        :type overwrite: bool
        :param overwrite: If the file should be overwritten
        """
        self.__generator = Generator(output_file_name, overwrite)

    def generate(self, exercise_number: int, args: list[int | tuple[int, int] | list[str]], parallel=False) -> None:
        """
        This method generates a single exercise
        :type exercise_number: int
        :param exercise_number: The number of the exercise
        :type args: list[int | tuple[int, int] | list[str]]
        :param args: The arguments for the exercise
        :return: None
        :raises: ValueError
        :raises: TypeError
        :raises: IndexError
        """

        # if parallel, we expect start number arguments. The threads themselves are spawened elsewhere
        if not parallel:
            self.__generator.generate(exercise_number, args)
        else:
            self.__generator.generate_parallel(exercise_number, args)

    @staticmethod
    def print_arguments(exercise_number: int) -> None:
        """
        This method prints the arguments for the exercise
        :type exercise_number: int
        :param exercise_number: The number of the exercise
        :return: None
        """
        Generator.print_arguments(exercise_number)
