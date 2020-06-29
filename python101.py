#!/usr/bin/env false
"""
Various notes on python for refresher
Not ment to be run as a script
"""
#--------------------------------------
# Differences between eval and exec
# eval : execute single dynamically generated expression,  returns the value
# exec : execute block of dynamically generated code, returns nothing
eval('37 + a')   # it is an expression
# Output: 42
exec('37 + a')
# No ouput
exec('a = 47')   # modify a global variable as a side effect
# No ouput, but now a=47

#--------------------------------------
# Input space seperated list of ints form keyboard
N = list(map(int, input().split(' ')))
# Input space seperated list of ints form keyboard, toss out first
N = list(map(int, input().split(' ')[1:]))
# Input strings into words
list_of_words = input().rstrip().split()
#--------------------------------------
# Recursion Anatomy:
# - base_case: exit condition, return a value
# - recursive_case: return call_Self()
# State:
# - pass in state,
# - make state global

# Stat: passed in state as n
def factorial(n):
  # BASE Case: exits recursion, returns state
  if n == 0:
    return 1  # Wacky factorial rule
  if n == 1:
    return n
  # RECURSIVE Case: calls self
  return n * factorial(n-1)

factorial(7)
#
# Generator to make list of lists
#

def listOfLists(n):
  if n:
    yield []
    yield from listOfLists(n-1)

print(list(listOfLists(4)))

# list of 0 or 1
# get all routes to end
# can only step on '0'
# can only step to n+1 or n+2
# SOLUTION: recurisive generator
def step_to_index(n, cur_list, c, last_n):
    cur_list.append(n)
    # Condition to leave
    if n == last_n:
        yield(cur_list)
    # Next steps
    step = n + 1
    if step <= last_n and c[step] == 0:
        yield from step_to_index(step, list(cur_list), c, last_n)
    # Next steps
    step = n + 2
    if step <= last_n and c[step] == 0:
        yield from step_to_index(step, list(cur_list), c, last_n)

c = [0, 1, 0, 1, 0, 1, 0, 1, 0]
last_n = len(c) -1
print(list(step_to_index(0, [], c, last_n)))
# OUPUT: [[0, 2, 4, 6, 8]]

c = [0, 1, 0, 0, 0, 1, 0, 1, 0]
last_n = len(c) -1
print(list(step_to_index(0, [], c, last_n)))
# OUPUT: [[0, 2, 3, 4, 6, 8], [0, 2, 4, 6, 8]]

#--------------------------------------
# bit O notation
#
# Lookup speed
# - O(n) for Array
# - O(1) for Associative Array (python dict, javsript object, perl hash, C++ map)
#
# O(1) means "it takes the same amount of time, no matter how big"
#
# NOTE: Might help to memorize the Sorting efficentcy... 
#         Worst    Best     Average
# Quick   O(n^2)   O(nlogn) O(nlogn)
# Merge:  O(nlogn) O(n)     O(nlogn)
# Bubble  O(n^2)   O(n)     O(n^2)
# Insert  O(n^2)   O(n)     O(n^2)
# Select  O(n^2)   O(n^2)   O(n^2)
#================================================
# time and dates
import datetime
d1='Sun 10 May 2015 13:54:36 -0700'
d2='Sun 10 May 2015 13:54:36 -0000'
ts2=datetime.datetime.strptime(d2, '%a %d %b %Y %H:%M:%S %z').timestamp()
ts1=datetime.datetime.strptime(d, '%a %d %b %Y %H:%M:%S %z').timestamp()
elapsed_sec = abs(ts1 - ts2)

#================================================
# zip
# - takes 2 iterables of length n
# - returns n tuples (shorter of two iterables)
#================================================
list(zip([1,2,3,4], ['a','b','c']))
# Out: [(1, 'a'), (2, 'b'), (3, 'c')]
response = map(''.join, zip(*[iter(string)]*max_width))
response = list(map('\n'.join, zip(*[iter(string)]*max_width)))

# trick: dict from 2 lists of equal size
list_1 = ["A","B","C"]
list_2 = [1,2,3]
dictionary = dict(zip(list_1, list_2))
# Out: {'B': 2, 'A': 1, 'C': 3}

#================================================
# map
# - takes function + list,
# - returns list of each element through function
# NOTE: better written as list comprehension.
#================================================
list(map(lambda i: i*3, [1,2,3,4]))
[3, 6, 9, 12]

list(map(int, ['1','2','3','4']))
[1, 2, 3, 4]

# Guido says it is better written in list comprehension
list(i*3 for i in [1,2,3,4])

#================================================
# filter
# - takes function + list,
# - returns list of items which function(item) is True.
# NOTE: better written as list comprehension.
#================================================
list(filter(lambda i: i>5, [2,3,5,6,7]))
[6,7]

list(x for x in [2,3,5,6,7] if i>5)

#================================================
# reduce  ****GONE FROM PYHTON 3: use for loop****
# - takes function + list
# - acumuliatively apply result to next item inlist
# - return one result.
#================================================
result = reduce( lambda x,y: x+y, [1,2,3,4,5])
15

# Guido says does not return a list, so it is not list comprehesnion

result = 0
for x in [1,2,3,4,5]:
   result += x
      
#================================================
# sorted
# - takes list or dict and function
# - order list by highest result of the function
# - return list, does not modify like list.sort()
#================================================
mydict = {'a':10, 'b':-2, 'c':5, 'd':0}
sorted(mydict, key=lambda key: mydict[key])
['b', 'd', 'c', 'a']

sorted([1,2,3,4,5], key=lambda x: -1*x)
[5, 4, 3, 2, 1]

# Compound list comprehension
[ \
    (i,j) \
    for i in range(3) \
    for j in {'a','b','c'} \
]
[(0, 'a'), (0, 'b'), (0, 'c'), 
 (1, 'a'), (1, 'b'), (1, 'c'), 
 (2, 'a'), (2, 'b'), (2, 'c')
 
#================================================
# try:      # small bit of code that could fail
# except:   # code to execute if try  block failed
# raise:    # recall the previous exception block
# else:     # runs, if try was successful
# finally:  # runs, no matter what outcome of try.
try:
    pass # some code
except IOError as e:
    pass
except ZeroDivisionError as e:
    pass
except Exception as e:
    print("some other error")
    raise e
else:
    print("No error occurred")
finally:
    print("Run this No matter what")

#================================================
# closures:
# - a function 
# - contains a function with private namespace variables 
#
# Namespace in nested functional program
#  local then global(which is really module namespace)
# !!! x only exists when function is runs
#
x="bla"
def foo():
    x = "a string"
    def inner():
        #global x # blunt hammer to use global scope
        x = "b"
        print(x)
    inner()
    print(x)

foo()
# Output:
#   b
#   a string

#================================================
# Decorators:
# - take a function
# - returns a function
# - Add clousre
# - Implemented with classes or closrues
#==========================================
def wraps(f):
    def inner(*args, **kwargs):
        print(args)
        print(kwargs)
        return f(*args, **kwargs)
    return inner

@wraps
def foo(x,y):
    return x + y

foo(2,3)
# Out:
# (2,3)
# {}
# 5

#================================================
# list comprehention
# - return a list
#
# 3 PARTS TO LIST COMPREHENTION
#  lookslike   where from         condition
#   ...       ................   ...............
# [ row       for row in data    if not 0 in row]
#
#================================================

# for 'row' in file
# 'split' string into array
# take 3rd element
# 'strip' whiitespace
# collect unique as a set
#
set([ row.split(",")[2].strip() for row in open("classmates.csv") ] )

set(['student3', 'student2', 'student1', 'instructor', 'bla'])

#==========================================
# generator
#==========================================
# a generator expression
# - is a Promisses to run in the future once -
# - use for performance, save memory (only uses one line at a time),
# - stores previous state
# - calls yield
# - caller calls <generator>.next()
#
# REF: David Beasly, "Generator For Sysadmins"
#==========================================

# generatator expression
g = (x for x in range(10))
print(sum(g)
      
# Wrap list comprehension in ()
genexp = ( row.split(",")[2].strip() for row in open("classmates.csv") )

)

# Generater functions
def genfunc():
    x = range(1,10)
    for i in x:
        yield i   # key word yield makes this a generator

# calling
f = genfunc()
for i in f:
    print i

def infinite():
    while True:
        yield 1

# Calling
g = infinite()
g.next()

def evens():
    """Generate even numbres"""
    n = 0
    while True:
        yield n
        n += 2

even_set = (next(evens) for _ in range(5))

#==========================================
# itertools module - Composition is the key
#==========================================
# REF: https://realpython.com/python-itertools/
#
# TERM: combinatorial explosion: a few inputs produce a large number of outcomes
# Brute force algorithms are suseptible:
#  combinations(), 
#  combinations_with_replacement()
#  permutations()

# Iterators are iterable:
list(map(sum, zip([1, 2, 3], [4, 5, 6])))

#BAD:
def naive_grouper(inputs, n):
    """Returns tuples"""
    num_groups = len(inputs) // n
    return [tuple(inputs[i*n:(i+1)*n]) for i in range(num_groups)]

# BETTER:  howerver zip drops any odd tiems that don't line up
def better_grouper(inputs, n):
    """Returns tuples"""
    # create list of n refs to same iterator object id
    iter_refs = [iter(inputs)] * n
    # iter() is an object with an mem address
    # [iter()]*n makes a list of n repated addresses
    # zip sees n lists pointing to the same id
    # zip takes the first item from ref1   (leaving [2:])
    #     takes the first item from ref2   (leaving [3:])
    #     ...
    #     takes the first item from ref(n) (leaving [n:])
    # zip makes a tuple of (item1, item2)
    return zip(*iter_refs)

#
# This is how hard it is to split string into chunks of max_width
# My God.
# Used range not enumerate
string = "this is a big string!"
max_width = 4
print ('\n'.join(list([ string[i:i+max_width] for i in range(0, len(string), max_width)])))
# Output:
# this
#  is 
# a bi
# g st
# ring
# !

## itertools zip_longest
# create iter object from string
# []*width makes a list of the same references to the iter object
# zip connects the elements of each list
#      since address of iter is the same, this joins chunks of width
# map calls join on each list from the zip_longest
# 
import itertools as it
string = "this is a big string!"
max_width = 4
iter_ref = [iter(string)]*max_width
words = (''.join(x) for x in it.zip_longest(*iter_ref, fillvalue=''))
for word in words:
    print(word)
# Output:
# this
#  is 
# a bi
# g st
# ring
# !

## itertools chain - chain iterators together
import itertools as it
a=[1,2,3]
b=[2,6,8]
c=[6,8,9]
print(list( i for i in it.chain(a,b,c)))
# Output:
# [1, 2, 3, 2, 6, 8, 6, 8, 9]

## groupby
import itertools as it
things = [
  ("animal", "bear"), 
  ("animal", "duck"), 
  ("plant", "cactus"), 
  ("vehicle", "speed boat"), 
  ("vehicle", "school bus")
]
for key, group in it.groupby(things, lambda x: x[0]):
  for thing in group:
    print("{} is a {}".format(thing[1], key))
# Output:
# bear is a animal
# duck is a animal
# cactus is a plant
# speed boat is a vehicle
# school bus is a vehicle

## itertools combinations
# Problem: You have 
#  three $20 dollar bills, 
#  five $10 dollar bills, 
#  two $5 dollar bills, 
#  and five $1 dollar bills. 
# How many ways can you make change for a $100 dollar bill?
#
# A choice of k things from a set of n things is called a combinations,
# it.combinations()
# - takes an iterable and positive integer n
# - returns iterator over cobinations of tuples of n
#
bills = [20, 20, 20, 10, 10, 10, 10, 10, 5, 5, 1, 1, 1, 1, 1]
makes_100 = []
for i in range(len(bills)):
    # combinations finds all combos of a given size i
    # sum: add elements of tuple
    # filter: tests for the condition
    # set removes repeat
    for z in set(filter(lambda x: sum(x) == 100, it.combinations(bills,i))):
        makes_100.append(z)

print(len(makes_100))
5

## itertools combinations_with_replacement
# How many ways are there to make change for a $100 bill using any number of
# $50, $20, $10, $5, and $1 dollar bills?
#
# You need a way to generate all possible combinations using any number of bills. 
# itertools.combinations_with_replacement()
# - takes an iterable and a positive integer n
# - returns an iterator over n-tuples of elements
# * The return allows elements to be repeated in the tuples it returns
#   e.g. all $1 bills
# - Won't have any duplicates
bills = [50, 20, 10, 5, 1]
makes_100 = []
for i in range(1,101):
    # combinations_with_replacement: All 96,560,645 combinations! from bills,  i long
    # sum each resulting set, and test for value
    # filter: reduce to matches
    for z in filter(lambda x: sum(x) == 100, it.combinations_with_replacement(bills,i)):
        makes_100.append(z)

print(len(makes_100))
#343

## itertools permutations
# - takes iterable and size
# - returns every permutation
# Another “brute force” 
#  n! = n * (n -1) * (n-1) * ... * 2 * 1
print(it.permutations('ABCD', 2))
# OUTPUT: AB AC AD BA BC BD CA CB CD DA DB DC

## ittertools count
# - takes optional start and step (float and negatives)
# - returns iterator
evens = it.count(step=2) # create iterator
even_set = list(next(evens) for _ in range(5)) # call it
count_down = it.count(start=10, step=-1) # create iterator
print(count_down)
# Output:
# [0, 2, 4, 6, 8]
ten_to_zero = list(next(count_down) for _ in range(10)) # call it
print(ten_to_zero)
# Output:
#  [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

list(zip(it.count(), ['a', 'b', 'c']))
# Output: 
# [(0, 'a'), (1, 'b'), (2, 'c')]

# Def: recurrence relation : describs a numeric sequence with a recursive formula
def fibs():
    """ second order recurrence relation because it looks back 2"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

#==========================================
# collections: 
# REF: https://docs.python.org/3/library/collections.html

from collections import namedtuple
Car = namedtuple('Car', 'color mileage')
my_car = Car('red', 3812.4)
print(my_car.color)
print(my_car.milage)

#==========================================
# collections: 
# REF: https://docs.python.org/3/library/collections.html#deque-objects
# double ended queue
from collections import deque
d = deque()
d.push(1)
d.pushleft(0)
d.pop()
d.rotate(1)
d.clear()
d.extendleft('abc')

## collections defaultdict
# Guarantees a key
# Sorting dictionary on key and value (if value is an int)
# dict iteritems became items in Py3, and the tuple in lambda 
s = 'ccbbbaade'
chars = collections.defaultdict(int)
for c in s:
    chars[c] += 1
for i in sorted(chars.items(), key=lambda kv: (-kv[1], kv[0]))[0:3]:
    print("{} {}".format(*i))

# Also see: collecitons.OrderedDict

#==========================================
# set:
# union, intersection, difference and symmetric difference operations,
engl_s='1 2 3 4 5 6 7 8 9'
french_s='10 1 2 3 11 21 55 6 8'
some_s='1 2 3 4'
eng_sub = set(map(int, engl_s.split()))
french_sub = set(map(int, french_s.split()))
some_sub= set(map(int, some_s.split()))
# set.issubset()
print( some_sub <= eng_sub )
# Intersection: in both English and French
print(len(eng_sub & french_sub))
#   5
# Difference: in only English
print(len(eng_sub - french_sub))
#   4
# Symmetric difference: in English or French, not both
print(len(eng_sub ^ french_sub))
# Mutating a set:
#  .update() or |=,
#  .insertion_update() or &=
#  .difference_update() or -=
#  .symetric_difference_update() or ^=
print(engl_s.issuperset(some_sub))

#==========================================
# regex
# REF: https://docs.python.org/3/howto/regex.html
import re
html = "<p>this that thoes</p>"
re.findall(r"<[^>]+>", html)
['<p>', '</p>']

re.sub(r"<(/|)p>", r"<\1foodles>", html)
'<foodles>this that thoes</foodles>'

import re
text = ''
for _ in range(int(input())):
    # Readinput, subtract comments
    text = re.sub(r'<!.+-->',r' ',(text+input()))

# Find HTML Tags (starts with <, followed by non / and multiple non > and ended with >)    
for er in re.findall(r'<([^/][^>]*)>', text):
    # when er is ' ',  seperate the tag, attribute, value
    if ' ' in er:
        #                        tag        attrib     value
        for ere in re.findall(r'([a-z]+)? *([a-z-]+)="([^"]+)', er):
            if ere[0]:
                print(ere[0])          
            print('-> '+ere[1]+' > '+ere[2])
    else:
        print(er)

# begins with 4,5,6
# sets of 4 ints
# optionaly seperated by ' ' or '-'
# 16 integers
# No more than 3 repeating ints
import re
cards = [
'7165863385679329',
'6175824393389297',
'5252248277877418',
'9563584181869815',
'5179123424576876'
]
card_pattern = r'^[4-6][0-9]{3}[ -]?([0-9]{4}[ -]?){3}$'
for card in cards:
    result = re.search(card_pattern, card)
    if result:
        all_digits = ''.join( c for c in card if c not in ' -' )
        result2 = re.search(r"(\w)\1\1\1", all_digits)
        if result2:
            print("Invalid") #:{}".format(card))
        else:
            print("Valid") #: {}".format(card))
    else:
        print("Invalid") #:{}".format(card))


# 100000 to 999999
# Avoid alternating repeat numbers with a look ahead
regex_integer_in_range = r"^[1-9]\d{5}$"
regex_alternating_repetitive_digit_pair = r"(\d)(?=\d\1)"

# remove some caracters only between letters,
# uses a look behind for a word, look ahead for a word, and the stuff in the middle
matrix_decoded = re.sub(r'(?<=\w)([@#$%!& ]{1,})(?=\w)', ' ', matrix_str)


# valid email:
import re
import email.utils
email_str = r'^[a-z][0-9a-z-\._]+@[a-z]+\.[a-z]{1,3}$'
email_regex = re.compile(email_str)
num_inputs = int(input())
test_input = []
for i in range(num_inputs):
     test_input.append(str(input()))
     
for input_str in test_input:
    parsed = email.utils.parseaddr(input_str)
    if not '' in parsed:
        if email_regex.search(parsed[1]):
            print("valid:{}".format(email.utils.formataddr(parsed)))


#================================================
from html.parser import HTMLParser
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print(tag)
        [print('-> {} > {}'.format(*attr)) for attr in attrs]
        
html = '\n'.join([input() for _ in range(int(input()))])
parser = MyHTMLParser()
parser.feed(html)
parser.close()

#================================================
# pytest
# https://docs.pytest.org/en/stable/getting-started.html
# https://docs.python.org/3/library/unittest.html
#

#================================================
# Distributing
#  https://setuptools.readthedocs.io/en/latest/setuptools.html
#  https://packaging.python.org/tutorials/packaging-projects/
#
mkdir -p packaging_tutorial/example_pkg/tests
touch packaging_tutorial/example_pkg/__init__.py
touch packaging_tutorial/{LICENSE,README.md,setup.py}
tree --charset ascii packaging_tutorial/
  packaging_tutorial/
  |-- example_pkg
  |   |-- __init__.py
  |   `-- tests
  |-- LICENSE
  |-- README.md
  `-- setup.py

cat > packaging_tutorial/setup.py <<'EOF'
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-YOUR-USERNAME-HERE", # distribution name of your package
    version="0.0.1",  # see PEP 440 https://www.python.org/dev/peps/pep-0440
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",  # one-sentence summary of the package
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    scripts=["say_hello.py"],

    scripts=["myapp.py"],
    
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=["docutils>=0.3"],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "stations": ["stations_example.json", "stations.json"],
        # And include any *.msg files found in the "hello" package, too:
        "hello": ["*.msg"],
    },
    
)
EOF

cat > packaging_tutorial/README.md <<'EOF'
# Example Package

This is a simple example package. You can use
[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.
EOF

cat > packaging_tutorial/LICENSE <<'EOF'
Copyright (c) 2018 The Python Packaging Authority

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

#
# Generate distribution archive
#
pushd packaging_tutorial
python3 setup.py sdist bdist_wheel
python3 setup.py bdist

#
# Look at the product
#
ls -alF dist/

    total 16
    drwxr-xr-x 2 jstile jstile 4096 Jun 10 15:32 ./
    drwxr-xr-x 6 jstile jstile 4096 Jun 10 15:32 ../
    -rw-r--r-- 1 jstile jstile 2515 Jun 10 15:32 example_pkg_YOUR_USERNAME_HERE-0.0.1-py3-none-any.whl
    -rw-r--r-- 1 jstile jstile 1197 Jun 10 15:32 example-pkg-YOUR-USERNAME-HERE-0.0.1.tar.gz

