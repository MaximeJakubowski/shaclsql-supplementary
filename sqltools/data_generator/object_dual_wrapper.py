import random


class ObjectDualWrapper:

    __objects: list[tuple[str, bool, bool]]

    def __init__(self):
        """
        Constructor
        """
        self.__objects = []

    def __len__(self):
        """
        This method returns the length of the list of objects
        :return: The length of the list of objects
        """
        return len(self.__objects)

    def __getitem__(self, item: int) -> tuple[str, bool, bool]:
        """
        This method returns the object at the given index
        :type item: int
        :param item: The index of the objects
        :return: The object at the given index
        """
        return self.__objects[item]

    def __setitem__(self, key, value):
        """
        This method sets the object at the given index
        :param key: The index of the object
        :param value: The new value of the object
        :return: None
        """
        self.__objects[key] = value

    def append(self, new_object: tuple[str, bool, bool]):
        """
        Appends an object to the list of objects
        :type new_object: tuple[str, bool, bool]
        :param new_object: The object to append
        """
        self.__objects.append(new_object)

    def get_object1(self) -> str:
        """
        This method returns a random object
        :return: A random object
        """
        start_index: int = random.randint(0, len(self.__objects) - 1)
        while self.__objects[start_index][1]:
            start_index = (start_index + 1) % len(self.__objects)
        self.__objects[start_index] = (self.__objects[start_index][0], True, self.__objects[start_index][2])
        return self.__objects[start_index][0]

    def get_object2(self) -> str:
        """
        This method returns a random object
        :return: A random object
        """
        start_index: int = random.randint(0, len(self.__objects) - 1)
        while self.__objects[start_index][2]:
            start_index = (start_index + 1) % len(self.__objects)
        self.__objects[start_index] = (self.__objects[start_index][0], self.__objects[start_index][1], True)
        return self.__objects[start_index][0]

    def reset(self):
        """
        This method resets the objects
        :return: None
        """
        my_object: int
        for my_object in range(len(self.__objects)):
            self.__objects[my_object] = (self.__objects[my_object][0], False, False)

    def contains(self, item: str) -> bool:
        """
        This method checks if the object is in the list
        :type item: str
        :param item: The object
        :rtype: bool
        :return: True if the object is in the list, False otherwise
        """
        for my_object in self.__objects:
            if my_object[0] == item:
                return True
        return False
