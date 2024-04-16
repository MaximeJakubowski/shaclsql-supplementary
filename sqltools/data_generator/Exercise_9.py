import math
import random
from data_generator import Exercise, FileIO, ObjectWrapper


class Exercise9(Exercise):

    __number_of_humans: int
    __objects: ObjectWrapper
    __languages: ObjectWrapper
    __range_of_objects: tuple[int, int]

    __start_humanid = 0
    __start_objectid = 0

    def __init__(self, file: FileIO, number_of_humans: int, number_of_objects: int, number_of_languages: int,
                 range_of_objects: tuple[int, int], start_humanid=0, start_objectid=0):
        """
        Constructor
        :type file: FileIO
        :param file: The abstract file class that gets shared over multiple classes.
        :type number_of_humans: int
        :param number_of_humans: The number of humans that will be generated
        :type number_of_objects: int
        :param number_of_objects: The number of objects that will be generated
        :type number_of_languages: int
        :param number_of_languages: The number of languages that will be generated (at least 1)
        :type range_of_objects: tuple[int, int]
        :param range_of_objects: The range of objects that will be generated
        :raises ValueError: If the range of objects is bigger than the number of objects
        :raises ValueError: If the range of objects is not correct
        :raises ValueError: If the number of objects is not correct
        :raises ValueError: If the number of humans is not correct
        :raises ValueError: If the range of languages is not correct
        :raises ValueError: If the range of languages is not correct
        :raises ValueError: If the languages are not correct
        """
        super().__init__(file)

        if range_of_objects[1] > number_of_objects:
            raise ValueError("The range of objects is bigger than the number of objects")
        if range_of_objects[0] > range_of_objects[1]:
            raise ValueError("The range of objects is not correct")
        if range_of_objects[0] < 0:
            raise ValueError("The range of objects is not correct")
        if number_of_objects < 0:
            raise ValueError("The number of objects is not correct")
        if number_of_humans < 0:
            raise ValueError("The number of humans is not correct")
        if number_of_languages < 1:
            raise ValueError("The number of languages is not correct")
        if number_of_languages > 676:
            raise ValueError("Maximal 676 languages")

        self.__objects = ObjectWrapper()
        self.__languages = ObjectWrapper()
        self.__number_of_humans = number_of_humans
        self.__range_of_objects = range_of_objects

        self.__start_humanid = start_humanid
        self.__start_objectid = start_objectid

        # More uniform language generator
        for first_letter in "abcdefghijklmnopqrtuvwxyz":
            for second_letter in "abcdefghijklmnopqrtuvwxyz":
                self.__languages.append((f"{first_letter}{second_letter}", False))
                if len(self.__languages) >= number_of_languages:
                    break
            if len(self.__languages) >= number_of_languages:
                break

        # length_languages: int = int(math.log(number_of_languages, 20)) + 1
        # # 20 is a bit less than the length of the alphabet (26)
        # # This gives us enough margin to generate enough languages
        # while number_of_languages > len(self.__languages):
        #     new_language: str = f"{self._gen_random_str(length_languages)}"
        #     if not self.__languages.contains(new_language):
        #         self.__languages.append((new_language, False))

        my_object: int
        for my_object in range(self.__start_objectid, self.__start_objectid + number_of_objects):
            self.__objects.append((f"\"Exercise9/object{my_object}\"@{self.__languages.get_object()}", False))
            self.__languages.reset()

    @staticmethod
    def print_arguments() -> None:
        """
        This method prints the arguments of the generator
        :return: None
        """
        Exercise.print_arguments()
        print("number_of_humans: int - The number of humans that should be generated")
        print("number_of_objects: int - The number of objects that should be generated")
        print("number_of_languages: int - The number of languages that should be generated (at least 1)")
        print("range_of_objects: tuple[int, int] - The range of objects that should be generated per human")

    def __gen_helper_objects(self, human_iri: str) -> None:
        """
        This method generates a random object
        :return: A random object
        """
        for _ in range(random.randint(self.__range_of_objects[0], self.__range_of_objects[1])):
            my_object: str = self.__objects.get_object()
            self._output_file.write(f"{human_iri} <http://example.com/firstName> {my_object} .\n")
        self.__objects.reset()

    def gen_ex(self) -> None:
        """
        This method executes the generator
        :return: None
        """
        self._output_file.write('\n')
        human: int
        for human in range(self.__start_humanid, self.__start_humanid + self.__number_of_humans):
            my_subject: str = self._gen_human(9, human)
            self.__gen_helper_objects(my_subject)
