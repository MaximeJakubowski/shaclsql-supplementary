import random
from data_generator import Exercise, FileIO, ObjectWrapper


class Exercise10(Exercise):

    __number_of_humans: int
    __start_dates: ObjectWrapper
    __end_dates: ObjectWrapper

    __start_humanid=0

    def __init__(self, file: FileIO, number_of_humans: int, range_number_of_start_dates: tuple[int, int],
                 range_number_of_end_dates: tuple[int, int], range_start_value: tuple[int, int],
                 range_end_value: tuple[int, int], start_humanid=0):
        """
        Constructor
        :type file: FileIO
        :param file: The abstract file class that gets shared over multiple classes.
        :type number_of_humans: int
        :param number_of_humans: The number of humans that will be generated
        :type range_number_of_start_dates: tuple[int, int]
        :param range_number_of_start_dates: The range of start dates that will be generated
        :type range_number_of_end_dates: tuple[int, int]
        :param range_number_of_end_dates: The range of end dates that will be generated
        :type range_start_value: tuple[int, int]
        :param range_start_value: The range of start values that will be generated
        :type range_end_value: tuple[int, int]
        :param range_end_value: The range of end values that will be generated
        :raises ValueError: If the range of start dates is not correct
        :raises ValueError: If the range of end dates is not correct
        :raises ValueError: If the number of humans is not correct
        :raises ValueError: If the range of start values is not correct
        :raises ValueError: If the range of end values is not correct
        """
        super().__init__(file)

        if range_number_of_start_dates[0] > range_number_of_start_dates[1]:
            raise ValueError("The range of start dates is not correct")
        if range_number_of_start_dates[0] < 0:
            raise ValueError("The range of start dates is not correct")
        if range_number_of_end_dates[0] > range_number_of_end_dates[1]:
            raise ValueError("The range of end dates is not correct")
        if range_number_of_end_dates[0] < 0:
            raise ValueError("The range of end dates is not correct")
        if number_of_humans < 0:
            raise ValueError("The number of humans is not correct")
        if range_start_value[0] > range_start_value[1]:
            raise ValueError("The range of start values is not correct")
        if range_start_value[0] < 0:
            raise ValueError("The range of start values is not correct")
        if range_end_value[0] > range_end_value[1]:
            raise ValueError("The range of end values is not correct")
        if range_end_value[0] < 0:
            raise ValueError("The range of end values is not correct")

        self.__start_dates = ObjectWrapper()
        self.__end_dates = ObjectWrapper()
        self.__number_of_humans = number_of_humans

        self.__start_humanid = start_humanid

        number_of_start_dates = random.randint(range_number_of_start_dates[0], range_number_of_start_dates[1])
        while number_of_start_dates > len(self.__start_dates):
            new_start_date: str = str(random.randint(range_start_value[0], range_start_value[1]))
            if not self.__start_dates.contains(new_start_date):
                self.__start_dates.append((new_start_date, False))

        number_of_end_dates = random.randint(range_number_of_end_dates[0], range_number_of_end_dates[1])
        while number_of_end_dates > len(self.__end_dates):
            new_end_date: str = str(random.randint(range_end_value[0], range_end_value[1]))
            if not self.__end_dates.contains(new_end_date):
                self.__end_dates.append((new_end_date, False))

    @staticmethod
    def print_arguments() -> None:
        """
        This method prints the arguments of the generator
        :return: None
        """
        Exercise.print_arguments()
        print("number_of_humans: int - The number of humans that should be generated")
        print("range_number_of_start_dates: tuple[int, int] - The amount of start dates that should be generated")
        print("range_number_of_end_dates: tuple[int, int] - The amount of end dates that should be generated")
        print("range_start_value: tuple[int, int] - The domain of the start values")
        print("range_end_value: tuple[int, int] - The domain of the end values")

    def __gen_helper_date(self, human_iri: str) -> None:
        """
        This method generates the dates for the human
        :type human_iri: str
        :param human_iri: The iri of the human
        :return: None
        """
        start_date: str = self.__start_dates.get_object()
        end_date: str = self.__end_dates.get_object()
        self._output_file.write(f"{human_iri} <http://example.com/startWork> \"{start_date}\" .\n")
        self._output_file.write(f"{human_iri} <http://example.com/endWork> \"{end_date}\" .\n")
        self.__start_dates.reset()
        self.__end_dates.reset()

    def gen_ex(self) -> None:
        """
        This method executes the generator
        :return: None
        """
        self._output_file.write('\n')
        human: int
        for human in range(self.__start_humanid, self.__start_humanid + self.__number_of_humans):
            my_subject: str = self._gen_human(10, human)
            self.__gen_helper_date(my_subject)
