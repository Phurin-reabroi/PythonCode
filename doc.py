
name = 'Dew'
print('Hello, ' + name + '!')

#Data types in Python
#-------------------------------------------
#String
text = 'Python is great!'

#Integer
number = 5

#Float
decimal = 3.14

#Boolean
has_money = True

#Tuples
coordinates = (10, 20)

#Lists
names = ['Alice', 'Bob', 'Charlie']

#Sets
unique_numbers = {1, 2, 3, 4, 5} 

#Dictionaries
users = {'Alice': 25, 'Bob': 30, 'Charlie': 35}

#-------------------------------------------

number = '100'
print(10 + int(number)) #Output: 110 

number = "ten"
print(10 + str(number)) #Output: 10ten TypeError: unsupported operand type(s) for +: 'int' and 'str'

#-------------------------------------------

#Type anatations
age: int = 25
name: str = 'Alice'
is_student: bool = True

#-------------------------------------------

#F -Strings
name = 'Alice'
age = 25
print(f'{name} is {age} years old.') #Output: Alice is 25 years old.

#-------------------------------------------
#Functions
def add(a: float, b: float) -> float:
    print(f'Adding {a} + {b}')
    return a + b
print(add(3.5, 2.5)) #Output: 6.0

def greet(name: str, greeting: str) -> None:
    print(f'{greeting}, {name}!')
greet('Alice', 'Hello') #Output: Hello, Alice!

def func() -> None:
    print('Hello, i am a function!')
func() #Output: Hello, i am a function!

#-------------------------------------------
#Loops
  #For loop
for i in range(5):
    print('Hello') #Output: Hello Hello Hello Hello Hello
for name in names:
    print(name) #Output: Alice Bob Charlie

  #While loop
i: int = 0
while i < 5:
    print(i) #Output: 0 1 2 3 4
    i += 1

#-------------------------------------------
#Comparison operators
a: int = 10
b: int = 20
print(a < b) #Output: True
print(a > b) #Output: False
print(a == b) #Output: False
print(a != b) #Output: True
print(a <= b) #Output: True
print(a >= b) #Output: False

#-------------------------------------------
#if elseif else statements
user_input: str = 'Hello'
if user_input == 'Hello':
    print('Hi there!')
elif user_input == 'how are you?':
    print('I am good, thanks!')
else:
    print('I am not sure how to respond.')
