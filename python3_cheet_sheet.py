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
# - takes 2 iterables
# - returns several tuples for each
#================================================
list(zip([1,2,3,4], ['a','b','c']))
[(1, 'a'), (2, 'b'), (3, 'c')]
response = map(''.join, zip(*[iter(string)]*max_width))
response = list(map('\n'.join, zip(*[iter(string)]*max_width)))

#================================================
# map
# - takes function + list,
# - returns list of each element through function
# NOTE: better written as list comprehension.
#================================================
list(map(lambda i: i*3, [1,2,3,4]))
[3, 6, 9, 12]

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
# reduce  ****NOT IN PYHTON 3: use for loop****
# - takes function + list
# - acumuliatively apply result to next item inlist
# - return one result.
#================================================
result = reduce( lambda x,y: x+y, [1,2,3,4,5])
15

# Replace:  List comprehesnion should only return a list 
result = 0
result+=x for x in [1,2,3,4,5]


#================================================
# sorted  
# - takes list or dict + function
# - order list by highest result of the function
# - return list    
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
# regex
import re
html = "<p>this that thoes</p>"
re.findall(r"<[^>]+>", html)
['<p>', '</p>']

re.sub(r"<(/|)p>", r"<\1foodles>", html)
'<foodles>this that thoes</foodles>'
#================================================
# Closures:
# - a function + enclosing scope
# - returns function objects that has private variables
#
# Namespace in nested functional program
#  local then global(which is really module namespace)
# !!! x only exists when function is runs
#
def foo():
    x = "a string"
    def inner():
        global x # blunt hammer
        x = "b"
        print(x)
    inner()
    print(x)

foo()
#================================================
# Decorators:
# - takes a function
# - returns a function and adding a clusre
# - wrapper around a function
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

def print_name(record):
    print record['fname']

#================================================
# list comprehention
#
# THERE ARE TREE PARTS TO LIST COMPREHENTION
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

# Wrap list comprehension in ()
genexp = ( row.split(",")[2].strip() for row in open("classmates.csv") )

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

# BETTER:  zip drops any odd tiems that don't line up
def better_grouper(inputs, n):
    """Returns tuples"""
    # create n refs to same iterator object id
    iter_refs = [iter(inputs)] * n
    # iter() is an object with an mem address
    # [iter()]*2 makes a list of  repated addresses
    # zip sees n lists pointing to the same id
    # zip takes the first item from ref1   (leaving [2:])
    #     takes the first item from ref2   (leaving [3:])
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


import itertools as it
it.zip_longest(iter(), fillvalue=1)

## chain - chain iterators together
a=[1,2,3]
b=[2,6,8]
c=[6,8,9]
print(list( i for i in it.chain(a,b,c)))
# Output:
# [1, 2, 3, 2, 6, 8, 6, 8, 9]

## groupby
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

## combinations
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
    # Set filters repeat cobinations
    for z in set(filter(lambda x: sum(x) == 100, it.combinations(bills,i))):
        makes_100.append(z)

print(len(makes_100))
5
#
# How many ways are there to make change for a $100 bill using any number of
# $50, $20, $10, $5, and $1 dollar bills?
#
# You need a way to generate all possible combinations using any number of bills. 
# itertools.combinations_with_replacement()
# - takes an iterable and a positive integer n
# - returns an iterator over n-tuples of elements
# * The return allows elements to be repeated in the tuples it returns
#   e.g. all $1 bills
# * The return won't have any duplicates
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

# it.permutations
# - takes iterable
# - returns every permutation
# Another “brute force” 
#  n! = n * (n -1) * (n-1) * ... * 2 * 1
# 

# it.count
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
# REF https://docs.python.org/3/library/collections.html#deque-objects
from collections import deque
d = deque()
d.push(1)
d.pushleft(0)
d.pop()
d.rotate(1)
d.clear()
d.extendleft('abc')

