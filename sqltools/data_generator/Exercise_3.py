import random
from data_generator import Exercise, FileIO, ObjectWrapper


class Exercise3(Exercise):

    __number_of_humans: int
    __friends: ObjectWrapper
    __companies: ObjectWrapper
    __range_of_friends: tuple[int, int]
    __range_of_companies: tuple[int, int]

    __start_humanid = 0
    __start_friendid = 0
    __start_companyid = 0

    def __init__(self, file: FileIO, number_of_humans: int, number_of_friends: int, number_of_companies: int,
                 range_of_friends: tuple[int, int], range_of_companies: tuple[int, int], start_humanid=0, start_friendid=0, start_companyid=0):
        """
        Constructor
        :type file: FileIO
        :param file: The abstract file class that gets shared over multiple classes.
        :type number_of_humans: int
        :param number_of_humans: The number of humans that will be generated
        :type number_of_friends: int
        :param number_of_friends: The number of friends that will be generated
        :type number_of_companies: int
        :param number_of_companies: The number of companies that will be generated
        :type range_of_friends: tuple[int, int]
        :param range_of_friends: The range of friends that will be generated
        :type range_of_companies: tuple[int, int]
        :param range_of_companies: The range of companies that will be generated
        :raises ValueError: If the range of friends is bigger than the number of friends
        :raises ValueError: If the range of companies is bigger than the number of companies
        :raises ValueError: If the range of friends is not correct
        :raises ValueError: If the range of companies is not correct
        :raises ValueError: If the number of friends is not correct
        :raises ValueError: If the number of companies is not correct
        """
        super().__init__(file)

        if range_of_friends[1] > number_of_friends:
            raise ValueError("The range of friends is bigger than the number of friends")
        if range_of_companies[1] > number_of_companies:
            raise ValueError("The range of companies is bigger than the number of companies")
        if range_of_friends[0] > range_of_friends[1]:
            raise ValueError("The range of friends is not correct")
        if range_of_companies[0] > range_of_companies[1]:
            raise ValueError("The range of companies is not correct")
        if range_of_friends[0] < 0:
            raise ValueError("The range of friends is not correct")
        if range_of_companies[0] < 0:
            raise ValueError("The range of companies is not correct")
        if number_of_friends < 0:
            raise ValueError("The number of friends is not correct")
        if number_of_companies < 0:
            raise ValueError("The number of companies is not correct")
        if number_of_humans < 0:
            raise ValueError("The number of humans is not correct")

        self.__friends = ObjectWrapper()
        self.__companies = ObjectWrapper()
        self.__number_of_humans = number_of_humans
        self.__range_of_friends = range_of_friends
        self.__range_of_companies = range_of_companies

        self.__start_humanid = start_humanid
        self.__start_friendid = start_friendid
        self.__start_companyid = start_companyid

        friend: int
        for friend in range(self.__start_friendid, self.__start_friendid + number_of_friends):
            self.__friends.append((f"<http://example.com/friend{friend}>", False))

        company: int
        for company in range(self.__start_companyid, self.__start_companyid + number_of_companies):
            self.__companies.append((f"<http://example.com/company{company}>", False))

    @staticmethod
    def print_arguments() -> None:
        """
        This method prints the arguments of the generator
        :return: None
        """
        Exercise.print_arguments()
        print("number_of_humans: int - The number of humans that should be generated")
        print("number_of_friends: int - The number of friends that should be generated")
        print("number_of_companies: int - The number of companies that should be generated")
        print("range_of_friends: tuple[int, int] - The range of friends that should be generated per human")
        print("range_of_companies: tuple[int, int] - The range of companies that should be generated her friend")

    def __gen_helper_companies(self, friend_iri: str) -> None:
        """
        This method will generate the companies for a friend
        :type friend_iri: str
        :param friend_iri: The friend that needs companies
        :return: None
        """
        for _ in range(random.randint(self.__range_of_companies[0], self.__range_of_companies[1])):
            company_iri: str = self.__companies.get_object()
            self._output_file.write(f"{friend_iri} <http://schema.org/CEO-of> {company_iri} .\n")
        self.__companies.reset()

    def __gen_helper_friends(self, human_iri: str) -> None:
        """
        This method will generate the friends for a human
        :type human_iri: str
        :param human_iri: The human that needs friends
        :return: None
        """
        for _ in range(random.randint(self.__range_of_friends[0], self.__range_of_friends[1])):
            friend_iri: str = self.__friends.get_object()
            self._output_file.write(f"{human_iri} <http://schema.org/friend> {friend_iri} .\n")
            #done before:
            #self.__gen_helper_companies(friend_iri)
        self.__friends.reset()

    def gen_ex(self) -> None:
        """
        This method executes the generator
        :return: None
        """
        self._output_file.write('\n')

        # first, gen for every possible friend (not human) a couple of CEO triples
        for friend in self.__friends:
            self.__gen_helper_companies(friend[0])

        # then assign friends to humans
        for human in range(self.__start_humanid, self.__start_humanid + self.__number_of_humans):
            human_iri = self._gen_human(3, human)
            self.__gen_helper_friends(human_iri)


        # human: int
        # for human in range(self.__start_humanid, self.__start_humanid + self.__number_of_humans):
        #     my_subject: str = self._gen_human(3, human)
        #     self.__gen_helper_friends(my_subject)
