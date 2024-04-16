import random
from data_generator import FileIO, Exercise, ObjectWrapper


class Exercise8(Exercise):

    __number_of_humans: int
    __objects: ObjectWrapper
    __range_of_objects: tuple[int, int]
    __probability_equal: int

    __prop1=""
    __prop2=""

    __start_humanid = 0
    __start_objectid = 0

    def __init__(self, file: FileIO, number_of_humans: int, number_of_objects: int,
                 range_of_objects: tuple[int, int], probability_equal: int, start_humanid=0, start_objectid=0):
        """
        Constructor
        :type file: FileIO
        :param file: The abstract file class that gets shared over multiple classes.
        :type number_of_humans: int
        :param number_of_humans: The number of humans that will be generated
        :type number_of_objects: int
        :param number_of_objects: The number of objects that will be generated
        :type range_of_objects: tuple[int, int]
        :param range_of_objects: The range of objects that will be generated
        :type probability_equal: int
        :param probability_equal: The probability of empty properties
        :raises ValueError: If the range of objects is bigger than the number of objects
        :raises ValueError: If the range of objects is not correct
        :raises ValueError: If the number of objects is not correct
        :raises ValueError: If the number of humans is not correct
        :raises ValueError: If the probability of empty properties is not correct
        :raises ValueError: If the number of properties is not correct
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
        if probability_equal < 0 or probability_equal > 100:
            raise ValueError("The probability of empty properties is not correct")

        self.__objects = ObjectWrapper()
        self.__number_of_humans = number_of_humans
        self.__range_of_objects = range_of_objects
        self.__probability_equal = probability_equal

        self.__start_humanid = start_humanid
        self.__start_objectid = start_objectid

        my_object: int
        for my_object in range(self.__start_objectid, self.__start_objectid + number_of_objects):
            self.__objects.append((f"<http://example.com/object{my_object}>", False))

        self.__prop1 = "<http://example.com/property1>"
        self.__prop2 = "<http://example.com/property2>"

    @staticmethod
    def print_arguments() -> None:
        """
        This method prints the arguments of the generator
        :return: None
        """
        Exercise.print_arguments()
        print("number_of_humans: int - The number of humans that should be generated")
        print("number_of_objects: int - The number of objects that should be generated")
        print("range_of_objects: tuple[int, int] - The range of objects that should be generated per property")
        print("probability_equal: int - The probability of equal properties (in percent)")

    def __gen_helper_objects(self, human_iri: str, property_iri: str) -> None:
        """
        This method generates the objects for a property
        :type human_iri: str
        :param human_iri: The IRI of the human
        :type property_iri: str
        :param property_iri: The IRI of the property
        :return: None
        """
        for _ in range(random.randint(self.__range_of_objects[0], self.__range_of_objects[1])):
            my_object: str = self.__objects.get_object()
            self._output_file.write(f"{human_iri} {property_iri} {my_object} .\n")
        self.__objects.reset()

    def __gen_helper_equal(self, human_iri: str) -> None:
        """
        This method generates the equal properties for a human
        :type human_iri: str
        :param human_iri: The IRI of the human
        :return: None
        """
        property_iri_1: str = self.__prop1
        property_iri_2: str = self.__prop2
        for _ in range(random.randint(self.__range_of_objects[0], self.__range_of_objects[1])):
            my_object: str = self.__objects.get_object()
            self._output_file.write(f"{human_iri} {property_iri_1} {my_object} .\n")
            self._output_file.write(f"{human_iri} {property_iri_2} {my_object} .\n")
        self.__objects.reset()

    def __gen_helper_properties(self, human_iri: str) -> None:
        """
        This method generates the properties for a human
        :type human_iri: str
        :param human_iri: The IRI of the human
        :return: None
        """
        if random.randint(0, 99) < self.__probability_equal:
            return self.__gen_helper_equal(human_iri)

        self.__gen_helper_objects(human_iri, self.__prop1) # random number of objects for prop1
        self.__gen_helper_objects(human_iri, self.__prop2) # random number of objects for prop2

    def gen_ex(self) -> None:
        """
        This method executes the generator
        :return: None
        """
        self._output_file.write('\n')
        human: int
        for human in range(self.__start_humanid, self.__start_humanid + self.__number_of_humans):
            my_subject: str = self._gen_human(8, human)
            self.__gen_helper_properties(my_subject)
