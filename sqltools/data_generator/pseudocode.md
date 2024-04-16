# Pseudo code data generator

## How to use the data_generator package
To make it easier to use the package, there is an interface available.
The interface is everything you need to get complete use of the package.
The interface has multiple functions. The most important function is generate; it will generate the data for one exercise.
However, it can run multiple times on the same file.

## how to import the package
Use the import statement: __from data_generator import GeneratorInterface__

## How to use the interface
The interface only consists out of non-static methods, so you do need to create an instance of the interface.
You can just use __Generator = GeneratorInterface(output_file_name)__  
Later you can call __Generator.generate(exercise_number, args)__.

### GeneratorInterface
GeneratorInterface(output_file_name, overwrite):  
&emsp;self.__generator = Generator(output_file_name, overwrite)

generate(self, exercise_number, args):  
&emsp;return self.__generator(exercise_number, args)

print_arguments(exercise_number):  
This method prints the help info about the arguments of the exercise.

### Generator
Generator(output_file_name, overwrite):  
&emsp;self.__output_file = FileIO(output_file_name, overwrite)

execute(self):  
This function will generate the data for all exercises, but the data is fixed.
This method is not meant to be used by the user, but by the interface.

generate(self, exercise_number, args):  
➡ Check exercise number  
➡ Create corresponding subclass of Exercise and give self.__output_file as an argument together with the other arguments.  
➡ Call gen_ex() on the subclass.  
➡ Return the result of gen_ex().

print_arguments(exercise_number):  
This method prints the help info about the arguments of the exercise.

### Exercise
Exercise(file):  
&emsp;self.__file = file

print_arguments():  
This method prints the help info about the arguments.

gen_ex(self):  
&emsp;Not implemented  
This function is implemented in the subclasses.
This function generates the data for a specific exercise.
_gen_object_time():  
generates a random time.

_gen_email(used_id):  
generates an email using the user id.

_gen_random_str(length):  
generates a random string with the given length.

_gen_random_int():  
generates a random integer.

_gen_human(number_of_exercise, human_id):
generates a human with the given id and exercise number.  
Writes it to the file.

### FileIO(file_name)
FileIO(file_name, overwrite):  
&emsp;self.__file_name = file_name  
&emsp;if overwrite:  
&emsp;&emsp;self.__file = open(file_name, 'w', encoding='utf-8')   
&emsp;else:  
&emsp;&emsp;self.__file = open(file_name, 'a', encoding='utf-8') 
File is automatically closed on destruction of object.

write(self, string):  
&emsp;self.__file.write(string)

### ObjectWrapper
ObjectWrapper():  
&emsp;self.__object = []

append(self, object):  
&emsp;self.__object.append(object)

get_object(self):  
returns a random object from the list.  
Marks the object as used so the object doesn't get picked a second time until after reset.

reset(self):  
resets the used objects.

### ObjectDualWrapper
ObjectDualWrapper():  
&emsp;self.__object = []

append(self, object):  
&emsp;self.__object.append(object)

get_object1(self):  
returns a random object from the list.  
Marks the object as used so the object doesn't get picked a second time (in the first list) until after reset.

get_object2(self):  
returns a random object from the list.  
Marks the object as used so the object doesn't get picked a second time (in the second list) until after reset.

reset(self):  
resets the used objects.

### Exercisei

Exercisei(file, args):  
&emsp;super().__ init __(file)  
➡ Store the args (note that the args are actually different for each exercise, but this is just an example).
In each exercise, the args are multiple arguments. Sometimes it is an inter, sometimes it is a tuple of 2 integer, sometimes it is a list of strings.
Each exercise uses a combination of these, look at the class for more info.

gen_ex(self):  
➡ Generate the data for the exercise.  
➡ Write the data to the file.

__gen_helper_*():
These methods are helpers to split the generation in multiple functions.

print_arguments():  
This method prints the help info about the arguments.

