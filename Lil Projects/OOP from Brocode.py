#Object Oriented Programming
import random



class Car:
    def __init__(self,model,year,color,is_working):
        self.model = model
        self.year = year
        self.color = color
        self.is_working = is_working

    def drive(self):
        print(f"{self.model} is driving...")

    def stop(self):
        print(f"{self.model} has stopped")

    def breakdown(self):
        if self.is_working == True:
            print(f"{self.model} is working")
        else:
            print(f"{self.model} is not working")
    def describe(self):
        print(f"The model : {self.model} ,The year: {self.year} , The color : {self.color} , Availability : {self.is_working}")

#car1 = Car("Mustang",2001,"blue",True)
#car2 = Car("Chevrolet","2023","Yellow",False)
#car3 = Car("BMW",2010,"Black",True)

#students = [student1,student2]
#for student in students:
    #pass






#CLASS VARIABLES



class Student:

    score = random.randint(50,100)
    graduation_year = 2020
    num_students = 0

    def __init__(self,name,age,school):
        self.name = name
        self.age = age
        self.school = school

        Student.num_students += 1

    def display(self):
        print(self.name)
        print(self.age)




#student1 = Student("Roy Mustang",21,"Upstate University")
#student2 = Student("Maes Hughes",22,"Downstate University")

#student1.display()
#print(Student.score)






#INHERITANCE
class Animal:
    def __init__(self,name):
        self.name = name
        self.is_alive = True

    def sounds(self):
        print(f"{self.name} sounds  ")
    def eat(self):
        print(f"{self.name} eats ")

    def sleep(self):
        print(f"{self.name} sleeps ")

class Dog(Animal):
    def speak(self):
        print("WOOF")
class Cat(Animal):
    def speak(self):
        print("MEOW")

class Mouse(Animal):
    def speak(self):
        print("SQUEEK")

class Schnauzer(Dog):
    pass

class Golden(Dog):
    pass

#dog = Dog("ODIN")
#cat1 = Cat("Roy")
#mouse1 = Mouse("Mustang")
#mouse1.speak()
#dog.speak()
#cat1.speak()





#MULTI LEVEL INHERİTANCE




class Prey:
    def __init__(self,name):
        self.name = name

    def flee(self):
        print("FLEE")

class Predator:
    def __init__(self,name):
        self.name = name

    def Hunt(self):
        print("HUNT")


class Lion(Predator):
    pass

class Fish(Prey,Predator):
    pass

#lion = Lion("Leon")
#fsh = Fish("AVG FİSH")
#fsh.Hunt()
#fsh.flee()
#print(fsh.name)
#print(lion.name)
#lion.Hunt()






#SUPER()



class Shape:
    def __init__(self,color,is_filled):
        self.color = color
        self.is_filled = is_filled
    def describe(self):
        print(f"This {self.color} shape is {"filled" if self.is_filled else "not filled"} ")

class Circle(Shape):
    def __init__(self,color,is_filled,radius):
        super().__init__(color,is_filled)
        self.radius = radius


class Square(Shape):
    def __init__(self,color,is_filled,width):
        super().__init__(color,is_filled)
        self.width = width


class Triangle(Shape):
    def __init__(self,color,is_filled,width,height):
        super().__init__(color,is_filled)
        self.width = width
        self.height = height


#tri = Triangle("red",True,5,5)
#circ = Circle("blue",False,3)
#square = Square("green",True,5)

#tri.describe()
#circ.describe()
#square.describe()







#STATIC METHODS(u only need to access the class not the object name)





class Employee:
    def __init__(self,name,position):
        self.name = name
        self.position = position

    def get_info(self):
        return f"{self.name} is {self.position}"

    @staticmethod
    def is_valid_position(position):
        valid_positions = ["Manager","Cashier","Cook","Janitor"]
        return position in valid_positions

#employee1 = Employee("AME","Cook")
#employee2 = Employee("OMAR","Janitor")
#print(employee1.get_info())
#print(employee2.get_info())
#print(Employee.is_valid_position("Scientist"))  #FALSE





#@Classmethod (cls)



class Student:
    count = 0
    total_gpa = 0

    def __init__(self,name,gpa):
        self.name = name
        self.gpa = gpa
        Student.count += 1
        Student.total_gpa += gpa

    def get_info(self):
        return f"{self.name} is {self.gpa}"

    @classmethod
    def get_count(cls):
        return f"number of students {cls.count}"

    @classmethod
    def get_total_gpa(cls):
        if cls.count == 0:
            return 0
        else:

            return f"Total Gpa is {cls.total_gpa / cls.count:.2f}"


#s1 = Student("AME",2.01)
#s2 = Student("OMAR",3.46)

#print(Student.get_count())
#s1.get_info()
#print(Student.get_total_gpa())





class Door:
    def __init__(self,mat,width,height,locked):
        self.mat = mat
        self.width = width
        self.height = height
        self.locked = locked

    def open(self):
        print("The Door is opened")
    def close(self):
        print("The Door is closed")

    def get_info(self):
        print(f"{self.mat} Door is {"locked" if self.locked else "unlocked"}")
        print(f"This door is {self.height}m tall and {self.width}m wide ")


    @staticmethod
    def valid_material(self):
        valid_mats = ["Oak","Iron","Cherry","Spruce"]
        if self.mat in valid_mats:
            return self.mat
        else:
            return "Ts door doesnt exists bro"


    @staticmethod
    def Break_door(self):
        a = int(input("How many pieces?: "))
        return f"The {self.mat} Door has broken into {a} pieces "



#d1 = Door("Oak",10,20,True)
#d2 = Door("Nigg",10,20,False)
#d2.get_info()
#print(Door.Break_door(d1))
##print(Door.valid_material(d1))
#print(Door.Break_door(d2))
#print(Door.valid_material(d2))











#Magic(DUNDER) methods


#__str__  -------> print(book1) diyince fonksiyonu printler

# __eq__ / __lt__ / __gt__  ----->  boolean functions (equal(==), little than(<), greater than(>))

#__add__(self,other)   -------> return f"{self.num_pages + other.num_pages}"

#__contains__(self,keyword)  -------> when u print it prints keyword aka Lion

#b1 = Book("The Lion King",...,...)
#return keyword in self.title or keyword in self.author
#print(Lion in b1)


#__getitem__(self,key)

#if key == "Title":
#    return self.tile
#elif key == "Author":
#    return self.author
#elif key == "num_pages"
#    return self.num_pages
#else:
#    return f"{key} was not found"

#print(book1["whatever u want the key"])












#@Property (can add additional logic when reading writing or deleting)



class Rectangle:
    def __init__(self,width,height):
        self._width = width
        self._height = height

    @property
    def width(self):
        return f"{self._width:.1f}cm"


    @property
    def height(self):
        return f"{self._height:.1f}cm"


    @height.setter
    def height(self,new_height):
        if new_height > 0:
            self._height = new_height
        else:
            print("The height must be greater than 0")


    @width.setter
    def width(self,new_width):
        if new_width > 0:
            self._width = new_width
        else:
            print("The width must be greater than 0")

    @height.deleter
    def height(self):
        del self._height
        print("height has been deleted")


    @width.deleter
    def width(self):
        del self._width
        print("width has been deleted")



#rectangle = Rectangle(3,6)
#print(rectangle.width)
#print(rectangle.height)

#rectangle.height = 5
#rectangle.width = 10

#del rectangle.height
#del rectangle.width






#DECORATOR(adding something to the base function on some occations)


def add_sprinkles(func):
    def wrapper(*args, **kwargs):
        print("you add sprinkles")
        func(*args,**kwargs)
    return wrapper


def add_fudge(func):
    def wrapper(*args,**kwargs):     #You have to add these or its an error if a parameter is given like flavor
        print("you add fudge")
        func(*args,**kwargs)
    return wrapper


@add_fudge
@add_sprinkles
def get_icecream(flavor):
    print(f"Here is your {flavor} Ice cream")

#get_icecream("nutella")







