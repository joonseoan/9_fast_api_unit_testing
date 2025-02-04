# [IMPORTANT]
# The function name should start with `test`
def test_equal_or_not_equal():
    # how we validate some types of data compared to another piece of data
    assert 3 == 3

    # we can test multiple tests
    assert 3 != 1

def test_is_instance():
    # [IMPORTANT]
    # isinstance() is a built-in Python function used to check
    # if an object is an instance of a specific class or type,
    # or a tuple of classes/types.

    # For example,
    # value = 3.14
    # print(isinstance(value, (int, float)))  # True, because 3.14 is a float

    # It returns True if the object is an instance of the specified class or type, and False otherwise.
    # isinstance() is more flexible than using type() because it accounts for inheritance
    # and can check against multiple types.

    # [IMPORTANT]
    # print(type(my_dog) == Dog)  # True
    # [Inheritance]
    # print(type(my_dog) == Animal)  # False because type can't be parent class
    # print(isinstance(my_dog, Animal))  # True because inheritance can be parent class

    # It is commonly used for type checking and validation in Python programs.
    assert isinstance('this is a string', str)
    assert not isinstance('10', int)


def test_boolean():
    validate = True
    assert validate is True
    # [IMPORTANT]
    # boolean with nested boolean
    assert ('hello' == 'world') is False


def test_type():
    # [IMPORTANT]
    # We can add boolean operation in type parameter
    assert type("hello" is str)
    assert type("world" is not int)


def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 19


def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]

    # [IMPORTANT]
    # "in" and "not in" can be used with `list`
    assert 1 in num_list
    assert 7 not in num_list

    """
        [IMPORTANT]
        The all() function in Python is a built-in function that takes an iterable (such as a list, tuple, or set) 
        as an argument and returns True if all elements in the iterable are truthy. If any element is falsy, 
        it returns False.

        Key Points:
        Truthy values: Values that are considered "true" in a Boolean context (e.g., 
        non-zero numbers, non-empty strings, non-empty lists, etc.).

        Falsy values: Values that are considered "false" in a Boolean context
        (e.g., 0, 0.0, None, False, empty strings "", empty lists [], {} etc.).
        (Empty sequences: "" (empty string), [] (empty list), () (empty tuple)) falsy but it is not related to all()
        # `all` function just looked at inside of [], (), {}, not themselves
        
        # Example 1: All elements are truthy
        list1 = [1, 2, 3, 4]
        print(all(list1))  # True, because all elements are non-zero (truthy)

        # Example 2: One element is falsy (0)
        list2 = [1, 2, 0, 4]
        print(all(list2))  # False, because 0 is falsy

        # Example 3: All elements are falsy
        list3 = [0, False, None]
        print(all(list3))  # False, because all elements are falsy

        # Example 4: Empty list
        list4 = []
        print(all(list4))  # True, because there are no falsy elements in an empty list
        
        numbers = [10, 20, 30, 40]
        if all(num > 0 for num in numbers):
            print("All numbers are positive.")
        else:
            print("Not all numbers are positive.")
        # Output: All numbers are positive.
        
        # Like javascript `map` function
        def is_even(n):
            return n % 2 == 0

        numbers = [2, 4, 6, 8]
        if all(map(is_even, numbers)):
            print("All numbers are even.")
        else:
            print("Not all numbers are even.")
        # Output: All numbers are even.
    """
    assert all(num_list)
    assert all([])

    """
        The any() function in Python is the counterpart to all().
        It takes an iterable (such as a list, tuple, or set) as an argument and returns True
        if at least one element in the iterable is truthy. 
        If all elements are falsy or the iterable is empty, it returns False.
        
        Key Points:
            Truthy values: Values that are considered "true" in a Boolean context 
            (e.g., non-zero numbers, non-empty strings, non-empty lists, etc.).

            Falsy values: Values that are considered "false" in a Boolean context 
            (e.g., 0, None, False, empty strings "", empty lists [], {}, {}, etc.).
            
        list1 = [1, 2, 3]
        print(any(list1))  # True, because all elements are truthy
        
        list2 = [0, False, 1]
        print(any(list2))  # True, because 1 is truthy
        
        list3 = [0, False, None]
        print(any(list3))  # False, because all elements are falsy
        
        empty_list = []
        print(any(empty_list))  # False, because there are no truthy elements
        
        numbers = [1, 3, 5, 8, 10]
        if any(num % 2 == 0 for num in numbers):
            print("At least one even number exists.")
        else:
            print("No even numbers.")
        # Output: At least one even number exists.
        
        def is_positive(n):
            return n > 0

        numbers = [-1, -2, 0, 3]
        if any(map(is_positive, numbers)):
            print("At least one positive number exists.")
        else:
            print("No positive numbers.")
        # Output: At least one positive number exists.
    """
    assert not any(any_list)


# ----------------------- pytest using object -----------------------
import pytest

class Employee:
    def __init__(self, first_name: str, last_name: str, department: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.years = years

# We can implement `fixture` to reuse and to share the same instance for each testing function.
# In other words, pytest `fixture` allows us to be able to instantiate the object and then pass it
# into out testing functionality.
# This runs automatically behind the scene, and then it allows us to have a kind of some dependency to our test
# which allows us less codes
@pytest.fixture
def default_employee():
    return Employee("John", "Doe", "Engineering", 3)


# We do not need to invoke `default_employee` because it works behind scene of `fixture`
def test_employee_initialization(default_employee):
    assert default_employee.first_name == "John", "First name should be John" # We can add a message
    assert default_employee.last_name == "Doe", "Last name should be Doe" # We can add a message
    assert default_employee.department == "Engineering"
    assert default_employee.years == 3


# Without `fixture` from pytest
# Sample
class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


def test_person_initialization():
    p = Student("John", "Doe", "Computer Science", 3)
    assert p.first_name == "John", "First name should be John" # We can add a message
    assert p.last_name == "Doe", "Last name should be Doe" # We can add a message
    assert p.major == "Computer Science"
    assert p.years == 3


