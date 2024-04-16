import random
from data_generator import Exercise, FileIO, ObjectWrapper


class Exercise2(Exercise):

    __number_of_humans: int
    __managers: ObjectWrapper
    __range_managers_per_human: tuple[int, int]

    __start_humanid=0
    __start_managerid=0

    def __init__(self, file: FileIO, number_of_humans: int, number_of_managers: int,
                 range_managers_per_human: tuple[int, int], start_humanid=0, start_managerid=0):
        """
        Constructor
        :type file: FileIO
        :param file: The abstract file class that gets shared over multiple classes.
        :type number_of_humans: int
        :param number_of_humans: The number of humans that should be generated
        :type number_of_managers: int
        :param number_of_managers: The number of managers that should be generated
        :type range_managers_per_human: tuple[int, int]
        :param range_managers_per_human: The range of managers that should be generated per human
        :raises ValueError: If the maximum number of managers per human is larger than the total number of managers
        :raises ValueError: If the minimum number of managers per human is smaller than 0
        :raises ValueError: If the range of managers per human is not correct
        :raises ValueError: If the number of managers is not correct
        :raises ValueError: If the number of humans is not correct
        """
        super().__init__(file)

        if range_managers_per_human[1] > number_of_managers:
            raise ValueError("The maximum number of managers per human is larger than the total number of managers")
        if range_managers_per_human[0] < 0:
            raise ValueError("The minimum number of managers per human is smaller than 0")
        if range_managers_per_human[0] > range_managers_per_human[1]:
            raise ValueError("The range of managers per human is not correct")
        if number_of_managers < 0:
            raise ValueError("The number of managers is not correct")
        if number_of_humans < 0:
            raise ValueError("The number of humans is not correct")

        self.__managers = ObjectWrapper()
        self.__number_of_humans = number_of_humans
        self.__range_managers_per_human = range_managers_per_human

        self.__start_humanid = start_humanid
        self.__start_managerid = start_managerid

        manager_index: int
        for manager_index in range(self.__start_managerid, self.__start_managerid + number_of_managers):
            self.__managers.append((f"<http://example.com/manager{manager_index}>", False))

    @staticmethod
    def print_arguments() -> None:
        """
        This method prints the arguments of the generator
        :return: None
        """
        Exercise.print_arguments()
        print("number_of_humans: int - The number of humans that should be generated")
        print("number_of_managers: int - The number of managers that should be generated")
        print("range_managers_per_human: tuple[int, int] - The range of managers that should be generated per human")

    def __gen_helper_manager(self, human_iri: str, threshold: int) -> None:
        """
        This method will generate the managers for a human
        :type human_iri: str
        :param human_iri: The IRI of the human
        :type threshold: int
        :param threshold: The number of managers that should be generated
        :return: None
        """
        for _ in range(threshold):
            my_object: str = self.__managers.get_object()
            self._output_file.write(f"{human_iri} <http://example.com/managed-by> \"{my_object}\" .\n")
        self.__managers.reset()

    def gen_ex(self) -> None:
        """
        This method executes the generator
        :return: None
        """
        self._output_file.write('\n')
        human: int
        for human in range(self.__start_humanid, self.__start_humanid + self.__number_of_humans):
            my_subject: str = super()._gen_human(2, human)
            threshold: int = random.randint(self.__range_managers_per_human[0], self.__range_managers_per_human[1] - 1)
            self.__gen_helper_manager(my_subject, threshold)
