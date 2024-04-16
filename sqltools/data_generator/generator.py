from data_generator import FileIO, Exercise1, Exercise2, Exercise3, Exercise4, Exercise5, Exercise6, \
    Exercise7, Exercise8, Exercise9, Exercise10


class Generator:  # Do not use this class directly, use GeneratorInterface instead. (see generator_interface.py)

    __output_file: FileIO

    def __init__(self, output_file_name: str, overwrite: bool = False):
        """
        Constructor
        :type output_file_name: str
        :param output_file_name: The name of the output file
        :type overwrite: bool
        :param overwrite: If the file should be overwritten
        """
        self.__output_file = FileIO(output_file_name, overwrite)

    def generate(self, exercise_number: int, args: list[int | tuple[int, int] | list[str]]) -> None:
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
        if exercise_number < 1 or exercise_number > 10:
            raise ValueError("Exercise number must be between 1 and 10")

        if exercise_number == 1:
            if len(args) != 6:
                raise ValueError("Shape 1 data  requires 6 arguments")
            Exercise1(self.__output_file, args[0], args[1], args[2], args[3], args[4], args[5]).gen_ex()
        if exercise_number == 2:
            if len(args) != 3:
                raise ValueError("Shape 2 data  requires 3 arguments")
            Exercise2(self.__output_file, args[0], args[1], args[2]).gen_ex()
        if exercise_number == 3:
            if len(args) != 5:
                raise ValueError("Shape 3 data  requires 5 arguments")
            Exercise3(self.__output_file, args[0], args[1], args[2], args[3], args[4]).gen_ex()
        if exercise_number == 4:
            if len(args) != 4:
                raise ValueError("Shape 4 data  requires 4 arguments")
            Exercise4(self.__output_file, args[0], args[1], args[2], args[3]).gen_ex()
        if exercise_number == 5:
            if len(args) != 5:
                raise ValueError("Shape 5 data  requires 5 arguments")
            Exercise5(self.__output_file, args[0], args[1], args[2], args[3], args[4]).gen_ex()
        if exercise_number == 6:
            if len(args) != 6:
                raise ValueError("Shape 6 data  requires 6 arguments")
            Exercise6(self.__output_file, args[0], args[1], args[2], args[3], args[4], args[5]).gen_ex()
        if exercise_number == 7:
            if len(args) != 6:
                raise ValueError("Shape 7 data  requires 6 arguments")
            Exercise7(self.__output_file, args[0], args[1], args[2], args[3], args[4], args[5]).gen_ex()
        if exercise_number == 8:
            if len(args) != 4:
                raise ValueError("Shape 8 data  requires 5 arguments")
            Exercise8(self.__output_file, args[0], args[1], args[2], args[3]).gen_ex()
        if exercise_number == 9:
            if len(args) != 4:
                raise ValueError("Shape 9 data  requires 4 arguments")
            Exercise9(self.__output_file, args[0], args[1], args[2], args[3]).gen_ex()
        if exercise_number == 10:
            if len(args) != 5:
                raise ValueError("Shape 10 data  requires 5 arguments")
            Exercise10(self.__output_file, args[0], args[1], args[2], args[3], args[4]).gen_ex()

    def generate_parallel(self, exercise_number: int, args: list[int | tuple[int, int] | list[str]]) -> None:
        # We expect more arguments here, compared to the non-parallel function

        if exercise_number < 1 or exercise_number > 10:
            raise ValueError("Exercise number must be between 1 and 10")

        if exercise_number == 1:
            Exercise1(self.__output_file, args[0], args[1], args[2], args[3], args[4], args[5], start_humanid=args[6], start_objects=args[7]).gen_ex()
        if exercise_number == 2:
            Exercise2(self.__output_file, args[0], args[1], args[2], start_humanid=args[3], start_managerid=args[4]).gen_ex()
        if exercise_number == 3:
            Exercise3(self.__output_file, args[0], args[1], args[2], args[3], args[4], start_humanid=args[5], start_companyid=args[6], start_friendid=args[7]).gen_ex()
        if exercise_number == 4:
            Exercise4(self.__output_file, args[0], args[1], args[2], args[3], start_humanid=args[4], start_friendcolid=args[5]).gen_ex()
        if exercise_number == 5:
            Exercise5(self.__output_file, args[0], args[1], args[2], args[3], args[4], start_humanid=args[5], start_objectid=args[6], start_propertyid=args[7]).gen_ex()
        if exercise_number == 6:
            Exercise6(self.__output_file, args[0], args[1], args[2], args[3], args[4], args[5], start_humanid=args[6], start_objectid=args[7]).gen_ex()
        if exercise_number == 7:
            Exercise7(self.__output_file, args[0], args[1], args[2], args[3], args[4], args[5], start_humanid=args[6], start_objectid=args[7]).gen_ex()
        if exercise_number == 8:
            Exercise8(self.__output_file, args[0], args[1], args[2], args[3], start_humanid=args[4], start_objectid=args[5]).gen_ex()
        if exercise_number == 9:
            Exercise9(self.__output_file, args[0], args[1], args[2], args[3], start_humanid=args[4], start_objectid=args[5]).gen_ex()
        if exercise_number == 10:
            Exercise10(self.__output_file, args[0], args[1], args[2], args[3], args[4], start_humanid=args[5]).gen_ex()

    @staticmethod
    def print_arguments(exercise_number: int) -> None:
        """
        This method prints the arguments of the generator
        :return: None
        """
        exercises = [
            Exercise1,
            Exercise2,
            Exercise3,
            Exercise4,
            Exercise5,
            Exercise6,
            Exercise7,
            Exercise8,
            Exercise9,
            Exercise10
        ]
        exercises[exercise_number - 1].print_arguments()


def run() -> None:
    """
    This function will run the generator.
    :return: None
    """
    output_file: str = str(f"../ttl_data/generated_rdf_data.ttl")
    Generator(output_file, True).generate(10, [20, (5, 10), (5, 10), (100, 150), (125, 175)])


if __name__ == "__main__":
    run()
