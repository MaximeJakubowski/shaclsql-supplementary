import random
from data_generator import Exercise, FileIO, ObjectWrapper


class Exercise6(Exercise):

    __number_of_humans: int
    __number_of_objects: int
    __probability_of_phone_number: int
    __probability_of_email: int
    __range_of_phone_numbers: tuple[int, int]
    __range_of_emails: tuple[int, int]
    __phone_numbers: ObjectWrapper
    __emails: ObjectWrapper

    __start_humanid=0
    __start_objectid=0

    def __init__(self, file: FileIO, number_of_humans: int, number_of_objects: int, probability_of_phone_number: int,
                 probability_of_email: int, range_of_phone_numbers: tuple[int, int], range_of_emails: tuple[int, int],
                 start_humanid=0, start_objectid=0):
        """
        Constructor
        :type file: FileIO
        :param file: The abstract file class that gets shared over multiple classes.
        :type number_of_humans: int
        :param number_of_humans: The number of humans that will be generated
        :type number_of_objects: int
        :param number_of_objects: The number of objects that will be generated (email and phone number separately)
        :type probability_of_phone_number: int
        :param probability_of_phone_number: The probability of a phone number being generated (in percent)
        :type probability_of_email: int
        :param probability_of_email: The probability of an email being generated (in percent)
        :type range_of_phone_numbers: tuple[int, int]
        :param range_of_phone_numbers: The range of phone numbers that will be generated
        :type range_of_emails: tuple[int, int]
        :param range_of_emails: The range of emails that will be generated
        :raises ValueError: If the number of humans is not correct
        :raises ValueError: If the number of objects is not correct
        :raises ValueError: If the probability of phone number is not correct
        :raises ValueError: If the probability of email is not correct
        :raises ValueError: If the range of phone numbers is not correct
        :raises ValueError: If the range of emails is not correct
        :raises ValueError: If the range of phone numbers is not correct
        :raises ValueError: If the range of emails is not correct
        """
        super().__init__(file)

        if number_of_humans < 0:
            raise ValueError("The number of humans is not correct")
        if number_of_objects < 0:
            raise ValueError("The number of objects is not correct")
        if probability_of_phone_number < 0 or probability_of_phone_number > 100:
            raise ValueError("The probability of phone number is not correct")
        if probability_of_email < 0 or probability_of_email > 100:
            raise ValueError("The probability of email is not correct")
        if range_of_phone_numbers[0] > range_of_phone_numbers[1]:
            raise ValueError("The range of phone numbers is not correct")
        if range_of_phone_numbers[0] < 0:
            raise ValueError("The range of phone numbers is not correct")
        if range_of_emails[0] > range_of_emails[1]:
            raise ValueError("The range of emails is not correct")
        if range_of_emails[0] < 0:
            raise ValueError("The range of emails is not correct")
        if range_of_phone_numbers[1] > number_of_objects:
            raise ValueError("The range of phone numbers is not correct")
        if range_of_emails[1] > number_of_objects:
            raise ValueError("The range of emails is not correct")

        self.__phone_numbers = ObjectWrapper()
        self.__emails = ObjectWrapper()
        self.__number_of_humans = number_of_humans
        self.__number_of_objects = number_of_objects
        self.__probability_of_phone_number = probability_of_phone_number
        self.__probability_of_email = probability_of_email
        self.__range_of_phone_numbers = range_of_phone_numbers
        self.__range_of_emails = range_of_emails

        self.__start_humanid = start_humanid
        self.__start_objectid = start_objectid

        for index in range(self.__start_objectid, self.__start_objectid + number_of_objects):
            self.__phone_numbers.append((f"\"{self._gen_random_int()} {index}\"", False))
            self.__emails.append((f"\"{super()._gen_email(index)}\"", False))

    @staticmethod
    def print_arguments() -> None:
        """
        This method prints the arguments of the generator
        :return: None
        """
        Exercise.print_arguments()
        print("number_of_humans: int - The number of humans that will be generated")
        print("number_of_objects: int - The number of objects that will be generated "
              "(email and phone number separately)")
        print("probability_of_phone_number: int - The probability of a phone number being generated for a human"
              " (in percent)")
        print("probability_of_email: int - The probability of an email being generated for a human"
              " (in percent)")
        print("range_of_phone_numbers: tuple[int, int] - The range of phone numbers that can be generated for a human")
        print("range_of_emails: tuple[int, int] - The range of emails that can be generated for a human")

    def __gen_helper_phone_numbers(self, human_iri: str) -> None:
        """
        This method generates the phone numbers for the human
        :type human_iri: str
        :param human_iri: The IRI of the human
        :return: None
        """
        if random.randint(0, 99) < self.__probability_of_phone_number:
            for _ in range(random.randint(self.__range_of_phone_numbers[0], self.__range_of_phone_numbers[1])):
                my_object: str = self.__phone_numbers.get_object()
                self._output_file.write(f"{human_iri} <http://example.com/phone> {my_object} .\n")
        self.__phone_numbers.reset()

    def __gen_helper_emails(self, human_iri: str) -> None:
        """
        This method generates the emails for the human
        :type human_iri: str
        :param human_iri: The IRI of the human
        :return: None
        """
        if random.randint(0, 99) < self.__probability_of_email:
            for _ in range(random.randint(self.__range_of_emails[0], self.__range_of_emails[1])):
                my_object: str = self.__emails.get_object()
                self._output_file.write(f"{human_iri} <http://example.com/email> {my_object} .\n")
        self.__emails.reset()

    def __gen_helper_objects(self, human_iri: str) -> None:
        """
        This method generates the objects for the human
        :type human_iri: str
        :param human_iri: The IRI of the human
        :return: None
        """
        self.__gen_helper_phone_numbers(human_iri)
        self.__gen_helper_emails(human_iri)

    def gen_ex(self) -> None:
        """
        This method executes the generator
        :return: None
        """
        self._output_file.write('\n')
        human: int
        for human in range(self.__start_humanid, self.__start_humanid + self.__number_of_humans):
            my_subject: str = super()._gen_human(6, human)
            self.__gen_helper_objects(my_subject)
