import time
import random
import string
import datetime
from data_generator import FileIO


class Exercise:
    """
    This class is the parent class of the exercises
    """

    _output_file: FileIO

    def __init__(self, file: FileIO):
        """
        Constructor
        :type file: FileIO
        :param file: The abstract file class that gets shared over multiple classes.
        """
        self._output_file = file

    @staticmethod
    def print_arguments() -> None:
        """
        This method prints the arguments of the generator
        :return: None
        """
        print("file: str - The path to the file that should be generated")

    def _gen_human(self, number_of_exercise: int, human_id: int) -> str:
        """
        This method helps the generator by executing the repeating part once.
        :rtype: str
        :return: Returns the subject used
        """
        my_subject: str = f"<http://example.com/human{number_of_exercise}_{human_id}>"
        self._output_file.write(f"{my_subject} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "
                                f"<http://example.com/human> .\n")
        return my_subject

    def gen_ex(self) -> None:
        """
        This method executes the generator
        :return: None
        :raises NotImplementedError: This method is not implemented, please implement it in the child class
        """
        raise NotImplementedError("This method is not implemented, please implement it in the child class")

    @staticmethod
    def _gen_random_int() -> int:
        """
        This function will generate a phone number.
        :rtype: int
        :return: A phone number
        """
        return int(time.time())

    @staticmethod
    def _gen_random_str(length: int) -> str:
        """
        This function will generate random string with length the length of the string
        :type length: int
        :param length: The length of the string
        :rtype: str
        :return: A random string of length: length
        """
        letters: str = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))

    @staticmethod
    def _gen_email(user_id: int) -> str:
        """
        This function will generate an email address
        :type user_id: int
        :param user_id: The id of the user
        :rtype: str
        :return: An email address
        """
        return f"user{user_id}@email.com"

    @staticmethod
    def _gen_object_time() -> str:
        """
        This function will generate a time.
        :rtype: str
        :return: The time
        """
        year = random.randint(1900, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        date_time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        return str(date_time.strftime("%Y-%m-%d_%H:%M:%S"))
