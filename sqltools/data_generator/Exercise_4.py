import random
from data_generator import Exercise, FileIO, ObjectDualWrapper


class Exercise4(Exercise):

    __number_of_humans: int
    __friendly_colleagues: ObjectDualWrapper
    __range_of_friends: tuple[int, int]
    __range_of_colleagues: tuple[int, int]

    __start_humanid=0
    __start_friendcolid=0

    def __init__(self, file: FileIO, number_of_humans: int, number_of_friends_and_colleagues: int,
                 range_of_friends: tuple[int, int], range_of_colleagues: tuple[int, int], start_humanid=0, start_friendcolid=0):
        """
        Constructor
        :type file: FileIO
        :param file: The abstract file class that gets shared over multiple classes.
        :type number_of_humans: int
        :param number_of_humans: The number of humans that will be generated
        :type number_of_friends_and_colleagues: int
        :param number_of_friends_and_colleagues: The number of friends or colleagues that will be generated
        :type range_of_friends: tuple[int, int]
        :param range_of_friends: The range of friends that will be generated
        :type range_of_colleagues: tuple[int, int]
        :param range_of_colleagues: The range of colleagues that will be generated
        :raises ValueError: If the range of friends is bigger than the number of friends and colleagues
        :raises ValueError: If the range of colleagues is bigger than the number of friends and colleagues
        :raises ValueError: If the range of friends is not correct
        :raises ValueError: If the range of colleagues is not correct
        :raises ValueError: If the number of friends and colleagues is not correct
        :raises ValueError: If the number of humans is not correct
        """
        super().__init__(file)

        if range_of_friends[1] > number_of_friends_and_colleagues:
            raise ValueError("The range of friends is bigger than the number of friends and colleagues")
        if range_of_colleagues[1] > number_of_friends_and_colleagues:
            raise ValueError("The range of colleagues is bigger than the number of friends and colleagues")
        if range_of_friends[0] > range_of_friends[1]:
            raise ValueError("The range of friends is not correct")
        if range_of_colleagues[0] > range_of_colleagues[1]:
            raise ValueError("The range of colleagues is not correct")
        if range_of_friends[0] < 0:
            raise ValueError("The range of friends is not correct")
        if range_of_colleagues[0] < 0:
            raise ValueError("The range of colleagues is not correct")
        if number_of_friends_and_colleagues < 0:
            raise ValueError("The number of friends and colleagues is not correct")
        if number_of_humans < 0:
            raise ValueError("The number of humans is not correct")

        self.__friendly_colleagues = ObjectDualWrapper()
        self.__number_of_humans = number_of_humans
        self.__range_of_friends = range_of_friends
        self.__range_of_colleagues = range_of_colleagues

        self.__start_humanid = start_humanid
        self.__start_friendcolid = start_friendcolid

        friendly_colleague: int
        for friendly_colleague in range(self.__start_friendcolid, self.__start_friendcolid + number_of_friends_and_colleagues):
            self.__friendly_colleagues.append((f"<http://example.com/friendlycolleague{friendly_colleague}>",
                                               False, False))

    @staticmethod
    def print_arguments() -> None:
        """
        This method prints the arguments of the generator
        :return: None
        """
        Exercise.print_arguments()
        print("number_of_humans: int - The number of humans that should be generated")
        print("number_of_friends_and_colleagues: int - The number of friends and colleagues that should be generated")
        print("range_of_friends: tuple[int, int] - The range of friends that should be generated per human")
        print("range_of_colleagues: tuple[int, int] - The range of colleagues that should be generated per human")

    def __gen_helper_friendly_colleague(self, human_iri: str) -> None:
        """
        This method will generate the friends and colleagues
        :type human_iri: str
        :param human_iri: The IRI of the human
        :return: None
        """
        for _ in range(random.randint(self.__range_of_friends[0], self.__range_of_friends[1])):
            self._output_file.write(f"{human_iri} <http://example.com/friend> "
                                    f"{self.__friendly_colleagues.get_object1()} .\n")
        for _ in range(random.randint(self.__range_of_colleagues[0], self.__range_of_colleagues[1])):
            self._output_file.write(f"{human_iri} <http://example.com/colleague> "
                                    f"{self.__friendly_colleagues.get_object2()} .\n")
        self.__friendly_colleagues.reset()

    def gen_ex(self) -> None:
        """
        This method executes the generator
        :return: None
        """
        self._output_file.write('\n')
        human: int
        for human in range(self.__start_humanid, self.__start_humanid + self.__number_of_humans):
            my_subject: str = self._gen_human(4, human)
            self.__gen_helper_friendly_colleague(my_subject)
