file1_content = """
import numpy as np

# Global variable in file1.py
GLOBAL_CONSTANT_1 = 10

def top_level_function1(x, y, z):
    return np.square(x) + y + z + GLOBAL_CONSTANT_1

class MyClass1:
    def __init__(self, value):
        self.value = value

    def square(self):
        return np.square(self.value) + GLOBAL_CONSTANT_1

    def cube(self):
        return np.power(self.value, 3) + GLOBAL_CONSTANT_1

    def sin(self):
        return np.sin(self.value) + GLOBAL_CONSTANT_1
        """

file2_content = """
from file1 import top_level_function1, MyClass1, GLOBAL_CONSTANT_1

# Global variable in file2.py
GLOBAL_CONSTANT_2 = 20

def top_level_function2(x):
    return top_level_function1(x) + GLOBAL_CONSTANT_2

class MyClass2:
    def __init__(self, value):
        self.my_class1 = MyClass1(value)

    def square_plus_constant(self):
        return self.my_class1.square() + GLOBAL_CONSTANT_2

    def cube_plus_constant(self):
        return self.my_class1.cube() + GLOBAL_CONSTANT_2

    def sin_plus_constant(self):
        return self.my_class1.sin() + GLOBAL_CONSTANT_2

# Example usage
if __name__ == "__main__":
    result1 = top_level_function2(5)
    print(result1)  # Output: 55

    obj2 = MyClass2(3)
    result2 = obj2.square_plus_constant()
    print(result2)  # Output: 39

    result3 = obj2.cube_plus_constant()
    print(result3)  # Output: 57

    result4 = obj2.sin_plus_constant()
    print(result4)  # Output: 20.141120008059867

    print(GLOBAL_CONSTANT_1)  # Output: 10
    print(GLOBAL_CONSTANT_2)  # Output: 20
        """
