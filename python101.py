#!/usr/bin/env python
"""
Various notes on python for refresher
Not ment to be run as a script
"""
#
# Python3 complexity of operations
#  https://www.ics.uci.edu/~pattis/ICS-33/lectures/complexitypython.txt
#
# Coding interview strategy and practice
# https://www.freecodecamp.org/news/coding-interviews-for-dummies-5e048933b82b/
#
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
# Find logest word without 3 contiguouse repeates
def solution(a, b, c):
  remaining = {'a': a, 'b': b, 'c': c}
  s = ''
  while True:
    took_character = False
    for c, n in sorted(remaining.items(), key=lambda x: x[1], reverse=True):
      if n > 0 and s[-2:] != (c + c):
        s += c
        remaining[c] = n - 1
        took_character = True
        continue
    if not took_character:
      return s

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
  if n <= 1:
    return 1  # Wacky factorial rule
  # RECURSIVE Case: calls self
  return n * factorial(n-1)

factorial(7)
#
# Generator to make list of lists
# NOTE: yield to iterate over large sequence, 
#       without storing entire sequence in memory.
#       to avoid MemoryError
# Using yield will result in a generator object.
# Using return will result in the first line of the file only.

# GENERATOR READ FILE:
def reader(file_name):
  with open(file_name, "r") as fh:
    for row in fh:
      yield row

# call
for i in reader(file_name):
  print(i, end="")
# Generator expression or generator comprehension
reader_gen = (row for row in open(file_name))

# INFINITE SEQUENCE
def infinite_seq():
  num = 0
  while True:
    yield num
    num += 1

inf_gen = infinite_seq()
next(inf_gen)
for i in infinite_seq():
  print(i, end=" ")

def listOfLists(n):
  if n:
    yield "a"  # New list
    yield from listOfLists(n-1)

print(list(listOfLists(4)))
mygen = listOfLists(4)
print(a for a in next(mygen))

# Profile with sys.getsizeof()
import sys
nums_squared_lc = [i * 2 for i in range(10000)]
sys.getsizeof(nums_squared_lc)
# 87624
nums_squared_gc = (i ** 2 for i in range(10000))
print(sys.getsizeof(nums_squared_gc))
# 120
# Profile with cProfile.run()
import cProfile
cProfile.run('sum([i * 2 for i in range(10000)])')


#-------------------------------
# Lists
#-------------------------------
# list of 0 or 1
# get all routes to end
# can only step on '0'
# can only step to n+1 or n+2
# SOLUTION: recurisive generator
def step_to_index(n, cur_list, c):
    last_n = len(c) -1
    cur_list.append(n)
    # Base case: Condition to leave
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
print(list(step_to_index(0, [], c)))
# OUPUT: [[0, 2, 4, 6, 8]]

c = [0, 1, 0, 0, 0, 1, 0, 1, 0]
print(list(step_to_index(0, [], c)))
# OUPUT: [[0, 2, 3, 4, 6, 8], [0, 2, 4, 6, 8]]

# Functional programming
# https://docs.python.org/3/howto/functional.html
# PYHTON Generators
# REF: https://realpython.com/introduction-to-python-generators/
# GENERATOR OBJECT METHODS
#    .send()
#    .throw()
#    .close()

    
def removeDuplicates(nums: List[int]) -> int:
    '''Removed dups from list
    Return new list length
    Change in place (id(nums) must not chagne)
    '''
    print(f"{id(nums)}")
    nums_len = len(nums)
    if nums_len <= 1:
        return nums_len
    x = 0
    while x < len(nums)-1:
        if nums[x] == nums[x+1]:
            nums.remove(nums[x])
        else:
            x += 1
    print(f"{id(nums)}")
    return(len(nums))

def maxProfit(prices: List[int]) -> int:
    '''You have array 'prices' of stock on given day
    You must alternate between buy<-->sell   (can't do one twice)
    1 <= prices.length <= 3 * 10 ^ 4
    0 <= prices[i] <= 10 ^ 4
    Input: [7,1,5,3,6,4] 
    Output: 7
    Input: [1,2,3,4,5]
    Output: 4
    Input: [7,6,4,3,1]
    Output: 0
    
    '''
    maxprofit = 0;
    plen=len(prices)
    for i in range(1, plen):
        print(f"today:{prices[i]} to yesterday:{prices[i-1]}")
        if prices[i] > prices[i-1]:
            print("toss yesterday, take todays")
            maxprofit += prices[i] - prices[i - 1];
    return maxprofit;
    '''
    today:1 to yesterday:7
    today:5 to yesterday:1
    toss yesterday, take todays: 4
    today:3 to yesterday:5
    today:6 to yesterday:3
    toss yesterday, take todays: 7
    today:4 to yesterday:6
    '''

def rotate(self, nums: List[int], k: int) -> None:
    """
    Rotate array in place, nums must keep same address
    """
    if k > len(nums):
        k= k%len(nums)

    # space and time O(n)
    tmp=nums[-k:]+nums[:-k]
    print(tmp1)
    print(nums)
    for i in range(len(nums)):
        nums[i] = tmp[i]
    
    # Space O(1)  Time O(n)
    for i in range(k):
        previous = nums[-1]
        for j in range(len(nums)): 
            nums[j], previous = previous, nums[j]

'''
Rotate Left:  zip(*m)           # top row becomes first row of all rows
Rotate right  zip(*reversed(m)) # top row becomes last row
Upside down:  reversed(m)       # bottom row becomes top
>>> pm(m)                   <=== original
 11 12 13 14
 21 22 23 24
 31 32 33 34
 41 42 43 44
>>> pm(zip(*m))             <=== Top becomes first row down
 11 21 31 41
 12 22 32 42
 13 23 33 43
 14 24 34 44
>>> pm(zip(*reversed(m)))  <=== Top becomes last row, down
 41 31 21 11
 42 32 22 12
 43 33 23 13
 44 34 24 14
>>> pm(reversed(m))       <=== Top becomes bottom, same order
 41 42 43 44
 31 32 33 34
 21 22 23 24
 11 12 13 14
 
 >>> for y in reversed([x for x in reversed(m)]):
...   print(f"{x},{y}")
... 
1,[11, 12, 13, 14]
1,[21, 22, 23, 24]
1,[31, 32, 33, 34]
1,[41, 42, 43, 44]

>>> for y in [x for x in reversed(m)]:
...   print(f"{x},{y}")
... 
1,[41, 42, 43, 44]
1,[31, 32, 33, 34]
1,[21, 22, 23, 24]
1,[11, 12, 13, 14]

>>> for y in reversed([x for x in m]):
...   print(f"{x},{y}")
... 
1,[41, 42, 43, 44]
1,[31, 32, 33, 34]
1,[21, 22, 23, 24]
1,[11, 12, 13, 14]

>>> for y in [x for x in m]:
...   print(f"{x},{y}")
... 
1,[11, 12, 13, 14]
1,[21, 22, 23, 24]
1,[31, 32, 33, 34]
1,[41, 42, 43, 44]

>>> for y in zip(*reversed([x for x in m])):
...   print(f"{x},{y}")
... 
1,(41, 31, 21, 11)
1,(42, 32, 22, 12)
1,(43, 33, 23, 13)
1,(44, 34, 24, 14)


Compound for statement 
[(x,y,z) 
   for x in range(1,30) 
   for y in range(x,30)
   for z in range(y,30)
  if x**2 + y**2 == z**2
]
[
 (3, 4, 5), (5, 12, 13), (6, 8, 10),
 (7, 24, 25), (8, 15, 17), (9, 12, 15), 
 (10, 24, 26), (12, 16, 20), (15, 20, 25), 
 (20, 21, 29)]
'''

def rotate_2d_matrix(self, matrix )->None:
    """Each  row becomes column.
    Rotate right in-place
    Original
    m = [  
       [ 5, 1, 9,11],
       [ 2, 4, 8,10],
       [13, 3, 6, 7],
       [15,14,12,16]
    ]
    routate right becomes:
    [
       [15,13, 2, 5],
       [14, 3, 4, 1],
       [12, 6, 8, 9],
       [16, 7,10,11]
    ]
    #========================================
    # Rotate Right
    for x in (zip(*reversed(m)): print(x)
     (15, 13, 2, 5), 
     (14, 3, 4, 1), 
     (12, 6, 8, 9), 
     (16, 7, 10, 11)
     
    # Rotate Left
    for x in list(zip(*m)): print(x)
     (5, 2, 13, 15)
     (1, 4, 3, 14)
     (9, 8, 6, 12)
     (11, 10, 7, 16)

    # Flip vertically, not horizontal
    for x in list(reversed(m)): print (x)
     [15, 14, 12, 16]
     [13, 3, 6, 7]
     [2, 4, 8, 10]
     [5, 1, 9, 11]
     
    # this is a rotate right
    # changed to tuple
    # replaced content of matrix
    """
    for i,x in enumerate((zip(*reversed(matrix)))):
        matrix[i] = list(x)
    

def containsDuplicate(self, nums: List[int]) -> bool:
    seen = {
    }
    for x in nums:
        if x not in seen:
            seen[x] = 1
            continue
        if x in seen:
            return True
    return False

def singleNumber(self, nums: List[int]) -> int:
    seen = {}
    for x in nums:
        if x not in seen:
            seen[x] = 1
            continue
        if x in seen:
            seen[x] += 1
    print(seen.items())
    return [ seen[0] for seen in seen.items() if seen[1] == 1][0]

def intersect(self, nums1: List[int], nums2: List[int]) -> List[int]:
    col1=collections.Counter(nums1)
    col2=collections.Counter(nums2)
    result = []
    for k,v in col1.items():
        if k in col2:
        quantity = min([v,col2[k]])
        result.extend([k]*quantity)
    return(result)

def plusOne(self, digits: List[int]) -> List[int]:
    # Join list of int into an int
    dig_str = ''.join(x for x in map(str,digits))
    dig_int = int(dig_str)
    # Increment by 1
    dig_int += 1
    # split back into a list of int
    digits = list(map(int,str(dig_int)))
    # return the nex list
    return digits

def plusOne(self, digits: List[int]) -> List[int]:
    # join list of int into int
    dig_int = int(''.join(list(map(str,digits)))) +1
    # split int into list of int
    return list(map(int,str(dig_int)))

def moveZeroes(self, nums: List[int]) -> None:
    """
    Do not return anything, modify nums in-place instead.
    """
    sub_ar = list(filter(lambda x: x!=0, nums))   
    len_sub_ar = len(sub_ar)
    for i in range(len(nums)):
        if i < len_sub_ar:
            nums[i] = sub_ar[i]
        else:
            nums[i] = 0    

def twoSum(self, nums: List[int], target: int) -> List[int]:
    d = {}
    for i in range(len(nums)):
        #print(i)
        # ##Shortcut
        # complement = target - nums[i]
        # print(f"i:{i}")
        # print(f"nums:{nums[i]}")
        # print(f"complement:{complement}")
        # if complement in d:
        #       print(f"===={d[complement][0], i}")
        #       return [d[complement][0], i]
        # Add value and nums index to hash 
        if nums[i] not in d:
        d[ nums[i] ] = [i]
        else:
        d[ nums[i] ].append(i)    

    # search for the mach
    # for each key, look for another key that hits the target
    for k in d.keys():
        complement = target - k      
        if complement in d:
            print("complement:{}".format(complement))
            if complement == k:
            print("same")
            if len(d[k]) == 2:
                print(f"{d[k]}")
                return d[k]
            else:
            print(
                f"k:{d[k]} "
                f"c:{d[complement]}"
            )
            return [ d[k][0], d[complement][0]  ]    

def isValidSudoku(self, board: List[List[str]]) -> bool:
    boxes = {}
    col = {}
    
    for i in range(9):  # Row
        
        row = []
        for j in range(9):  # Col
        
        cell = board[i][j]
        if j not in col:
                col[j] = []
                
        if cell != '.':
            num = int(cell)
            if  num  < 0 or num > 9:
            print("false")
            return False
            box_id = (i // 3 ) * 3 + j // 3
            if box_id not in boxes:
                boxes[box_id] = [num]
            else:
                if num in boxes[box_id]:
                    print("false")
                    return False
                else:      
                    boxes[box_id].append(num) 
            if num in row:
                print("false")
                return False
            else:
                row.append(num)
            
            
            if num in col[j]:
                print("false")
                return False
            else:
                col[j].append(num) 
                
            #print(f"box_id:{box_id}, digits:{ boxes[box_id]}")
            print(f"col:{col}")
        # Row ended
        print(f"row:{row}")
    # Col ended
    #board loaded, test if every box has at lease one digit
    for k,v in boxes.items():
        if len(v) ==0:
            print("false")
            return False 
    print("true")
    return True  


#------------------------------------
# String
#------------------------------------
    def shift_left(self, s: List[str]) -> None:
        """
        Do not return anything, modify s in-place instead.
        """
        # looop
        # store current in temp
        # move ahead to old
        # next iteration
        tmp = s[0]
        s_ln = len(s)
        for i in range(s_ln - 1):
            s[i] = s[i+1]
        s[-1] = tmp
        
def reverseString(self, s: List[str]) -> None:
    """
    Do not return anything, modify s in-place instead.
    """
    for i,x in enumerate(s[::-1]):
        s[i] = x

def reverse(self, x: int) -> int:
    """ modulo can pick off powers of 10.
    reverse the int x
    on  32bit overflow and return 0
    """
    rev = 0
    
    switch_sig = False
    if x < 0:
        switch_sig = True
    
    x = abs(x)
    while x > 0:
        rev = rev*10 + x%10
        x = x//10
    
    if switch_sig:
        rev *= -1
        
    if(abs(rev) > (2 ** 31 - 1)): # abs(sum) > (1 << 31) - 1):
        return 0
    else:
        return rev

def firstUniqChar(self, s: str) -> int:
    """return the first non-repeated char
    hashtable could be list of dict, to maintain order
    
    """
    index = -1
    chars = {}
    len_s = len(s)
    for i in range(len_s):
        if s[i] not in chars:
            chars[s[i]] = {'index': i, 'count': 1}
        else:
            chars[s[i]]['count'] += 1
    print(chars)
    # find first index with count of 1        
    for k,v in sorted(chars.items(), key=lambda kv: kv[1]['index']):
        if v['count'] == 1:
            return v['index']
    return index

def isAnagram(s: str, t: str) -> bool
    if len(s) != len(t):
        return False
    foo =  {}
    s_sort = ''.join(sorted(s))
    t_sort = ''.join(sorted(t))
    if  s_sort == t_sort:
        return True
    else:
        return False


def makeChange(coins, owed: int):
    """
    owed = 95
    coins = {1: 10, 5: 4, 10: 20, 25: 5, 50: 1, 100: 1}
    """
    if owed <= 0:
        return
    # Move coins into change
    change = {}
    # Track total value of register
    register = sum(k * v for k, v in coins.items())
    # Iterate over the coins until change is made
    for denom, qty in sorted(coins.items(), reverse=True):
        take_another = True
        while take_another:
            # test to stop loop
            if owed >= denom and qty > 0:
                owed -= denom
                register -= denom
                coins[denom] -= 1
                if not change.get(denom):
                    change[denom] = 1
                else:
                    change[denom] += 1
            else:
                take_another = False
                continue
    # End of register
    if owed == 0:
        print(
            "MADE CHANGE:\n"
            f"\tcoins: {coins}\n"
            f"\tregister: {register}\n"
            f"\towed: {owed}\n"
            f"\tchange: {change}"
        )
    elif register < owed:
        print(f"Call manager! owe:{owed}, have:{register}")      
    else:
        print(
            "Cant Make ChangeE:\n"
            f"\tcoins: {coins}\n"
            f"\tregister: {register}\n"
            f"\towed: {owed}\n"
            f"\tchange: {change}"
        )      

###
## I could not figure this one out.
###
#  str.isalpha() all letters
#  str.isnumeric() if all numeric
#  str.isalnum()  is letter and numbers

def isPalindrome(self, s: str) -> bool:
    filtered_chars = filter(lambda ch: ch.isalnum(), s)
    lowercase_filtered_chars = map(lambda ch: ch.lower(), filtered_chars)

    filtered_chars_list = list(lowercase_filtered_chars)
    reversed_chars_list = filtered_chars_list[::-1]

    return filtered_chars_list == reversed_chars_list        

32-bit signed integer range: [−231,  231 − 1].

#--------------------------------------
# constant time" or "O(1)"

list(s*n).count('a')
#  Memory Error
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


#----------------------------------------
'''
The count-and-say sequence is the sequence of integers with the first five terms as following:

1.     1
2.     11
3.     21
4.     1  2  11
5.     11 12 21

1 is read off as "one 1" or 11.
11 is read off as "two 1s" or 21.
21 is read off as "one 2, then one 1" or 1211.

Given an integer n where 1 ≤ n ≤ 30, generate the nth term of the count-and-say sequence. You can do so recursively, in other words from the previous member read off the digits, counting the number of digits in groups of the same digit.

Note: Each term of the sequence of integers will be represented as a string.

'''
def recurse_say(self, s):
    count_and_char = []
    current_char = s[0]
    current_count = 0    
    for i in range(len(s)):
        if current_char == s[i]:
            # same char
            current_count += 1
            continue
        else:
            # changed, so record count
            count_and_char.extend([str(current_count), current_char])
            current_char = s[i]
            current_count = 1
    # final 
    count_and_char.extend([str(current_count), current_char])    
    # done processing
    print(count_and_char)
    return ''.join(count_and_char)

def countAndSay(self, n: int) -> str:
    say = "1"
    for i in range(n - 1):  # 1, 2, 3, ,4
        say = self.recurse_say(say)
    return say
    
#-----------------------------------------------
# No solition to this problem
#-----------------------------------------------
# Implement atoi which converts a string to an integer.

# The function first discards as many whitespace characters as necessary until the first non-whitespace character is found. Then, starting from this character, takes an optional initial plus or minus sign followed by as many numerical digits as possible, and interprets them as a numerical value.
# T
# TThe string can contain additional characters after those that form the integral number, which are ignored and have no effect on the behavior of this function.
# T
# TIf the first sequence of non-whitespace characters in str is not a valid integral number, or if no such sequence exists because either str is empty or it contains only whitespace characters, no conversion is performed.
# T
# TIf no valid conversion could be performed, a zero value is returned.
#
# Only the space character ' ' is considered as whitespace character.
# Assume we are dealing with an environment which could only store integers within the 32-bit signed integer range: [−231,  231 − 1]. If the numerical value is out of the range of representable values, INT_MAX (231 − 1) or INT_MIN (−231) is returned.
#
def myAtoi(self, str: str) -> int:
    input_string = str
    index = 0
    isPositive = True
    result = 0

    # skip all leading spaces
    while index < len(input_string) and input_string[index] == ' ':
        index += 1

    # handle the +/-
    if index < len(input_string) :
        if input_string[index] == '+':
            index += 1
        elif input_string[index] == '-':
            isPositive = False
            index += 1

    # it's all digits until we stop
    while index < len(input_string) and input_string[index].isdigit() :
        result *= 10
        result += int(input_string[index])
        # lame version of overflow
        if result >= 2**31 :
            return 2**31 -1 if isPositive else -2**31
        index += 1
    return result if isPositive else -result

def atoi(text):
    return int(text) if text.isdigit() else text

def strStr(self, haystack: str, needle: str) -> int:
    """Returns index of needle in haystack
        or -1
    """
    # haystack='this is a big haystack'
    # neelde='hays'
    if needle == '':
        print("empty needle")
        return 0
    if len(haystack) < len(needle):
        print("needle too large")
        return -1
    # Build chars lookup table
    h_hash = {}
    for i,c in  enumerate(haystack):
        if c not in h_hash:
            h_hash[c] = [i]
        else:
            h_hash[c].append(i)

    needle_len = len(needle)
    # needle = ['a,'b','c']
    # needle = ['a,'a','a']
    # needle = ['z']
    #
    # Search in haystac from indicies list
    #   h_hash[needle[0]]  (e.g. ) h_hash['a'] = [2,10,20]
    if needle[0] not in h_hash:
        print("Needle not in haystack")
        return -1
    hay_index_list = h_hash[needle[0]]
    for h_index in hay_index_list:
        # needle sticking out of haystack
        if h_index + needle_len > len(haystack):
            print("bad needle")
            continue
        # Compare needle to haystack
        test_needle = ''.join(haystack[h_index:h_index+needle_len])
        if test_needle == needle:
            return h_index
    return -1

def can_make_note(magazine, note):
  counts = {}
  for word in magazine:
    if word not in counts:
      counts[word] = 1
    else:
      counts[word] += 1
  for word in note:
    if count.get(word, 0) == 0:
      return False
    count[word] -= 1
  return True

def solution(a, b, c):
  remaining = {'a': a, 'b': b, 'c': c}
  s = ''
  while True:
    took_character = False
    for c, n in sorted(remaining.items(), key=lambda x: x[1], reverse=True):
      if n > 0 and s[-2:] != (c + c):
        s += c
        remaining[c] = n - 1
        took_character = True
        break
    if not took_character:
      return s

def longestCommonPrefix(strs: List[str]) -> str:
    """
    return the longest common prefix among strings
    if none, return ''
    Input:   ["dog","racecar","car"]
    Output:  ""
    Input: ["flower","flow","flight"]
    Output: "fl"
    
    ["", "", ""] 
    
    """
    # O(n) (number of input strings)
    strs_sizes = (len(x) for x in strs)
    if not all(strs_sizes):
        print("empty string, no chance")
        return ""
    
    # loop over first set of chars by index
    # test match, if not return
    # - Need to not step off bounds
    prefix = ""
    for x in zip(*strs):
        if all(y==x[0][0] for y in x):
            prefix += x[0][0]
        else:
            break
    return prefix

def isPalindrome(s: str) -> bool:
    # strip non-alpha-nums and to-lower all chars    
    #
    right = (len(s) -1)
    # O(n/2)
    for left,c in enumerate(s):
        if left >= right:
            break
        rightC = s[right]
        leftC = s[left];

        # Index thought 
        if s[left] != s[right]:
            return False;
        left++
        right--



# ==================================
# Definition for singly-linked list.
# Added sir metheod 
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
    def __str__(self):
        return (
            f"val:{self.val}"
            f" => {self.next}"
        )

def removeNthFromEnd(head: ListNode, n: int) -> ListNode:
    '''  **** NOT WORKING ****
    Given a linked list, 
        remove the n-th node from the end of list 
        return its head
        n is always valid
        e.g. Input: 1->2->3->4->5, and n = 2.
        Result 1->2->3->5.
    '''
    # Create list of nodes, so we can find the depth and ref to object by index
    if n <= 0:
        return head
    
    # Store nodes in indexable list
    nodes=[]
    cur = head
    # walk list and turn it into an array
    while cur:
        nodes.append(cur)
        cur = cur.next

    if n > len(nodes):
        return head
    
    target = -1 * n  # use to index from the back of 
    print(f"target:{target}")
    targetNode = nodes[target]
    
    if targetNode:
        print(f"target-node:{targetNode}")
        # Does target node have a next (not the tail node)
        
        # removing node from linked list = prev-node.next = node.next 
        # nodes[target - 1].ndex = nodes[target].next
        # 1 -> 2 -> 3 -> 4 -> 5
        # remove (2) from the tail of the list
        # 1 -> 2 -> 3 -> 5
        
        # ronr HEAD IS A SPECIAL CASE
        if targetNode == head:
            head = targetNode.next
        else:
            # bypass the node we want to remove
            nodes[target - 1].next = targetNode.next
        targetNode.next = None
    else:
        print("Node is None")
    
    print(f"{head}")
    return head

ll = (ListNode(val=1,next=ListNode(val=2,next=ListNode(val=3,next=ListNode(val=4,next=ListNode(val=5))))))
ll_two = (ListNode(val=1,next=ListNode(val=2)))
ll_one = (ListNode(val=1))
ll_empty = ()

print(f"list after remove - {removeNthFromEnd(ll, 2)}")
print(f"ll_empty  - {removeNthFromEnd(ll_empty, 1)}")
print(f"ll_one  - {removeNthFromEnd(ll_one, 1)}")
print(f"ll_two  - {removeNthFromEnd(ll_two, 2)}")
    
def deleteNode(self, node):
    """
    Delete node from linked list
    :type node: ListNode
    :rtype: void Do not return anything, modify node in-place instead.

    Input: head = [4,5,1,9], node = 5
    Output: [4,1,9]
    
    Input: head = [4,5,1,9], node = 1
    Output: [4,5,9]
    
    A linked list node has everything it needs to delete it self
    """
    print(f"{node}")
    node.val = node.next.val
    node.next = node.next.next
    print(f"{node}")
    
def reverse_list(head: ListNode) -> ListNode:
    if not head:
        return head
    
    prev = None
    cur = head
    final = head
    keep_going = True
    while cur:
        next_node = cur.next     # Hang on to next element
        cur.next = prev          # Assign backward reference to current
        prev = cur               # Assign previous to current, for next round
        cur = next_node          # restore 
    # Ad the end cur points to the end of the original
    print("Done")
    return prev
ll = (ListNode(val=1,next=ListNode(val=2,next=ListNode(val=3,next=ListNode(val=4,next=ListNode(val=5))))))
# Now ll points to the end of the list.
# Must re-assign to have ll point to the new head
ll = reverse_list(ll)
print(f"yay: prev:{ll}")
# last:val:5 => val:4 => val:3 => val:2 => val:1 => None
ll = reverse_list(ll)                                                      
# last:val:1 => None
print(f"yay: prev:{ll}")


def reverse_list2(head: ListNode) -> ListNode:
    cur = head
    prev = None   # << to get past the first while
    while cur:
        save_next = cur.next  # Save next
        cur.next = prev       # Reverse next
        prev = cur            # Advance part1
        cur = save_next       # Advance part2
    
    print(f"prev:{prev}")
    head = prev
    # return head  # Not needed since we modified the object

ll = (ListNode(val=1,next=ListNode(val=2,next=ListNode(val=3,next=ListNode(val=4,next=ListNode(val=5)))))
)

l2 = reverse_list2(ll)
l3 = reverse_list2(l2)

#---------------------------------------------------------------
#
def alternate(s):
    """given a string, 
    create the longest string possible 
    that contains just two alternating letters, 
    by tossing out the others, 
    but you can't reorder the characters
    e.g. s='beabeefeab', result: babab
    
    # Strategy:
    # 1. Find unique chars
    # 2. Find all combinations, for in for, only add unique, non-repeating
    # 3. Make all lists from combos
    # 4. 
    """
    print(f"original: s:{s}")
    s_set= set(s)
    combos = []
    for i in s_set: # O(n)
        for j in s_set: # O(n) - O(n^2)
            if i+j in combos: 
                continue
            if i == j:
                continue
            combos.append(i+j)
    print(f"combos:{combos}")
    possible = []
    for pair in combos:
        s2 = ''.join(c for c in s if c in pair)
        if pair[0]*2 not in s2 and pair[1]*2 not in s2 :
            possible.append(s2)
    poss_sorted = sorted( possible, key=lambda x: len(x), reverse=True) 

    if len(poss_sorted) == 0:
        return 0
    print(poss_sorted[0])
    return len(poss_sorted[0])
# -----------------------------------------------
def mergeTwoLists( l1, l2):
    if l1 is None:
        return l2
    elif l2 is None:
        return l1
    elif l1.val < l2.val:
        l1.next = self.mergeTwoLists(l1.next, l2)
        return l1
    else:
        l2.next = self.mergeTwoLists(l1, l2.next)
        return l2

def mergeTwoLists( l1,l2):
    if l1 is None:
        return l2
    elif l2 is None:
        return l1
    # unchanged ref to node head
    prehead = ListNode(-1)      # Final ref to head
    prev = prehead              # moving pointer
    while l1 and l2:
        if l1.val <= l2.val:
            prev.next = l1      # assign 
            l1 = l1.next        # step forwad
        else:
            prev.next = l2      # assign
            l2 = l2.next        # step forwad
        # setp new list forward
        prev = prev.next
    # Pick up the remainder
    prev.next = l1 or  l2
    # send back the first item in the prehead
    return prehead.next

def merge(nums1, m, nums2, n):
    """
    :type nums1: List[int]
    :type m: int
    :type nums2: List[int]
    :type n: int
    :rtype: void Do not return anything, modify nums1 in-place instead.
    """
    # Make a copy of nums1.
    nums1_copy = nums1[:m] 
    nums1[:] = []

    # Two get pointers for nums1_copy and nums2.
    p1 = 0 
    p2 = 0
    
    # Compare elements from nums1_copy and nums2
    # and add the smallest one into nums1.
    while p1 < m and p2 < n: 
        if nums1_copy[p1] < nums2[p2]: 
            nums1.append(nums1_copy[p1])
            p1 += 1
        else:
            nums1.append(nums2[p2])
            p2 += 1

    # if there are still elements to add
    if p1 < m: 
        nums1[p1 + p2:] = nums1_copy[p1:]
    if p2 < n:
        nums1[p1 + p2:] = nums2[p2:]

def merge(nums1, m, nums2, n):
    """
    :type nums1: List[int]
    :type m: int
    :type nums2: List[int]
    :type n: int
    :rtype: void Do not return anything, modify nums1 in-place instead.
    """
    # two get pointers for nums1 and nums2
    p1 = m - 1
    p2 = n - 1
    # set pointer for nums1
    p = m + n - 1
    
    # while there are still elements to compare
    while p1 >= 0 and p2 >= 0:
        if nums1[p1] < nums2[p2]:
            nums1[p] = nums2[p2]
            p2 -= 1
        else:
            nums1[p] =  nums1[p1]
            p1 -= 1
        p -= 1
    
    # add missing elements from nums2
    nums1[:p2 + 1] = nums2[:p2 + 1]
    
def firstBadVersion(n):
    """
    :type n: int
    :rtype: int
    """
    left = 1
    right = n
    while(left < right):
        mid = left + (right - left)//2
        if isBadVersion(mid):
            right = mid
        else:
            left = mid +1
    return left
# -----------------------------------------------
def palendrome_single_linked_list(sllist: ListNode) -> bool:
    if sllist is None:
        return True
    response = True
    array_list = []
    # Make array list to get half-way point
    while sllist:
        array_list.append(sllist.val)
        sllist = sllist.next
    # Two pointer technique
    half = len(array_list)//2
    for i in range(half):
        if i == half:
            break
        if array_list[i] != array_list[ -1 - i ]:
            response = False
            break
    return response


ll_false = (ListNode(val=1,next=ListNode(val=10,next=ListNode(val=6,next=ListNode(val=4,next=ListNode(val=5)))))
)

ll_true_odd = (ListNode(val=1,next=ListNode(val=2,next=ListNode(val=6,next=ListNode(val=2,next=ListNode(val=1)))))
)

ll_true_even = (ListNode(val=1,next=ListNode(val=2,next=ListNode(val=6,next=ListNode(val=2,next=ListNode(val=1)))))
)

ll_one = (ListNode(val=0))

ll_empty = ()

tests = {
  'll_false:'   : ll_false,
  'll_true_odd:': ll_true_odd,
  'll_true_even': ll_true_even,
  'll_one:'     :ll_one,
  'll_empty:'   : ll_empty
}

for k,v in tests.items():
    print(f"{k:<5}" f"{palendrome_single_linked_list(v)}")
    
-------------------------------------------------------------------------
def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
    """two non-empty linked lists representing two non-negative integers.
    stored in reverse order
    each of their nodes contain a single digit.
    Add the two numbers and return it as a linked list.
    Input: (2 -> 4 -> 3) + (5 -> 6 -> 4)
    Output: 7 -> 0 -> 8
    Explanation: 342 + 465 = 807.
    """
    '''
    accum = 0;
    pow = 1;
    while True:
       digit1 = l1;
        digit2 = l2;
        if (digit1) accum += digit1.val * pow; digit1 = digit1.next;
        if (digit2) accum += digit2.val * pow; digit2 = digit2.next;
        pow *= 10;
        if !digit1 && !digit2: break;
    
    result = string(accum)
    result_in_reverse = result[::1]
    
    '''
    prev = None
    respone = ListNode(
        val = 0
    )
    
    if not l1 or not l2:
        return respone
    num1 = num2 = 0
    pow = 1
    while l1:
        num1 += l1.val * pow
        pow = pow * 10
        l1 = l1.next
    print(f"num1:{num1}")
    pow = 1
    while l2:
        num2 += l2.val * pow
        pow = pow * 10
        l2 = l2.next
    print(f"num2:{num2}")
    
    if num1 == 0 and  num2 == 0:
        return ListNode(0)
    
    num3 = num1 + num2
    num3_str = str(num3)
    print(f"num3:{num3}")
    num3_str = str(num3)[::-1]
    print(f"num3_str:{num3_str}")
    
    prehead = ListNode(-1)
    prev = prehead
    for i,c in enumerate(num3_str):
        tmp = ListNode(c)
        prev.next=tmp
        prev = prev.next
        
    print(prehead.next)
    return prehead.next

# will work
--------------------------------------------------
def hasCycle(head: ListNode) -> bool:
    """
    Given a linked list, determine if it has a cycle in it.
        'pos' is 0 index where tail connects
        No cycle pos = -1
        Input: head = [3,2,0,-4], pos = 1
        Output: true
        Input: head = [1,2], pos = 0
        Output: true
        BONUS: Solve it using O(1) memory?
    """        
    cur = head
    if not head:
        return False
    nodes = set()
    index = 0
    while cur:
        if cur in nodes:
            print(f"index:{index}")
            return True
        nodes.add(cur)
        cur = cur.next
        index +=1
    return False

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

# Loop until no values are zero
while all(value != 0 for value in your_dict.values())

#=================================================================
#
# Linked Lists
#
class Node:
    def __init__(self, cargo=None, next=None):
        self.cargo = cargo
        self.next  = next

    def __str__(self):
        return str(self.cargo)
    
def print_list(node):
    while node is not None:
        print(node, end=" ")
        node = node.next
    print()

def print_backward(list):
    # Base case
    if list is None:
        return
    head = list
    tail = list.next
    print_backward(tail)
    print(head, end=" ")

#=================================================================
#
# Count unival trees
# 
class Node:
    def __init__(self, value=None, right=None, left=None):
        self.value = value
        self.right = right
        self.left = left
        
    def __str__(self):
        return str(self.value)

    
def count_unival(root):
  total_count, is_unival = helper(root)
  return total_coun
  
def helper(root):
    if root == null:
        return(0,True) # 0 non-empty subtrees
           
    left_count, is_left_unival = helper(root.right)    
    right_count, is_right_unival = helper(root.left)
    
    is_unival = True
    
    if not is_left_unival or not is_right_unival:
        is_unival = False    
    
    if root.left != null and root.left.value != root.value
        is_unival = False
        
    if root.right != null and root.right.value != root.value
        is_unival = False
    
    if is_unival:
        return (left_count + right_count + 1, True)
    
    else:
        return (left_count + right_count, False)

#================================================
# Binary tree nodes (has data, left, right)
# FULL Tree:     node: 2 or 0 children
# COMPLETE Tree: left side fills before right
# PERFECT Tree:  all leaves on same level, COMPLETE AND FULL
# unival Tree:   all have the same value, except leafe childern can be Null
#
# Question Policy:   L<-N->R
#  In-Order   Pre-Order  Post-Order (where is N)
#   L->N->R   N->L->R     L->R->N 
#
# Node visit: handle value if value, do some work
# Left visit: handle   "if left, go left"
# Right visit: handle   "if right, go right"
#
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def insert(val, node):
    """Question Policy: In-Order"""
    if val <= node.data:
        if node.left:
            insert(val,node.left)
        else:
            node.left = TreeNode(val=val)
    else:
        if node.right:
            insert(val,node.right)
        else:
            node.right = TreeNode(val=val)
            
def contains(val, node):
    """Question Policy: In-Order"""
    if val == node.val:
        return True
    if val <= node.val:
        if not node.left:
            return False
        else:
            return contains(val, node.left)
    else:
        if not node.right:
            return False
        else:
            return contains(val, node.right)
    else:
        return False
    
def print_in_order(node):
    """Question Policy: In-Order"""
    if node.left:
        print_in_order(node.left)
    print(node.val)
    if node.right:
        print_in_order(node.right)
    print(node.val)

def max_depth(node):
    """Not sure about this"""
    depth  = -1
    left = right = 0
    if node.left:
        left -= max_depth(node.left)
    if node.right:
        right -= max_depth(node.right)
    if left >= right:
        depth = depth + left
    else:
        depth = depth + right
    return depth


def maxDepth(root: TreeNode) -> int:
    '''Find binary tree maximum depth.
    Input: [3,9,20,null,null,15,7]
    Return: 3
    '''
    depth  = 1
    left = right = 0
    if not root :
        return 0
    if root and root.left:
        left += root.maxDepth(root.left)
    if root and root.right:
        right += root.maxDepth(root.right)
    if left >= right:
        depth = depth + left
    else:
        depth = depth + right
    return depth

def is_unival(node):
    '''Tree is a unival tree if
    the children have a val = parent, or None
    '''
        
    
#================================================
#
# Cheep way to create hash table of array.
# could be used for finding stuff in the array
#
# Usage: lookup in dict is O(1)  <= more efficent
#        lookup in array is O(n)
#
a = [1,4, 2, 6, 88, 5, 3]
d = {x:0 for x in a}

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
# reduce  ****GONE FROM PYHTON 3 stdlib: use for loop****
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
      
import functtoos.reduce as reduce
reduce(lambda x: x>1,
result = reduce( lambda x,y: x+y, [1,2,3,4,5])
print(result)


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

# Convert for loop into a generator expression
  for word in note:
    if magazine.count(word) < note.count(word):
      print("No")
      break
  print("Yes")

# Test if Note words are in Magazine
def checkMagazine(magazine, note):
  counts = {}
  for word in magazine:
    if word not in counts:
      counts[word] =1
    else:
      counts[word] +=1

  for word in note:
    if counts.get(word, 0) == 0:
      print( "No")
      return
    counts[word] -= 1
  print( "Yes")

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
def fibonacci():
    """ second order recurrence relation because it looks back 2
    1,2,3,
    """
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

for x in range(n):
    result=next(next_fib)

fibonacci witout generator
n=1    
a, b = 0,1
for _ in range(n):
    a, b = b, a + b
return b

def maxProfit(m):
    best_profit = 0
    best_buy_index = None
    best_sell_index = None
    market_len = len(market)

    for buy_index in range(market_len):
        buy_value = market[buy_index]
        
        # sell has to be after buy
        for sell_index in range(buy_index+1,market_len,1):
            sell_value = market[sell_index]
            test_profit = sell_value - buy_value

        # is this profit the best?
        if test_profit > best_profit: 
            best_profit = test_profit
            best_buy_index = buy_index
            best_sell_index = sell_index
            
    return(best_profit)    
        
market = [7,6,4,3,1]
print(maxProfit(market))  


# Shift
l = [1,2,3,5,6]
# shift  left (front to end)
l.append(l.pop(0))
# shift right (end to front)
l[0:0] = l.pop()
# Reverse in place
l[:] = l[::-1]

# RON NOTES
# ok, looking at
# shift data to the right
next_item = nums1[n1_i+1]
for x in range(n1_i,len(nums1)-1, 1):
    tmp =  nums1[n1_i+1]
    nums1[n1_i+1] = nums1[n1_i]
    next_item = tmp

# nieve solution
def rob(self, nums: List[int]) -> int:
    odd = 0
    even = 0
    l  = len(nums)
    for i in range(0,l,2):
        even += nums[i]
    for i in range(1,l,2):
        odd += nums[i]

    if even > odd:
        return even
    else:
        return odd
        
#==========================================
# collections: 
# REF: https://docs.python.org/3/library/collections.html

# Python 3.7 dictionary order is guaranteed
nums = [0, 1, 2, 3, 4, 4, 5, 3, 2, 1, 0]
from collections import OrderedDict
od = OrderedDict()
#Assignment:
od["foo"] = ["bar"]
for cp, cp_data in info_query.iteritems():
if iteration not in self.glitch_test_summary:
    self.glitch_test_summary[iteration] = [glitch_test_summary_details]
else:
    self.glitch_test_summary[iteration].append(glitch_test_summary_details)
# Make dict with list value as key, positions as list of index
for i in range(len(nums)):
    if nums[i] not in od:
        od[i] = [nums[i]]
    else:
        od[i].append(nums[i])


from collections import Counter
count = 0
s = 'ffff'
len_s = len(s)
for i in range(1, len_s+1):  # count from 1 to the length
    print(f"i:{i}")
    for j in range(len_s-i): # 
        substr = "".join(sorted(s[j:j+i]))
        print(f"j:{j}, i:{i}: {substr}")
    a = ["".join(sorted(s[j:j+i])) for j in range(len_s-i+1)]
    print(a)
    b = Counter(a)
    for j in b:
        count+=b[j]*(b[j]-1)/2
return int(count)


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

d.append(1)
d.append(2)
# deque([1, 2])

d.appendleft(0)
# deque([0, 1, 2])

d.pop()
d.popleft()
d.rotate(1)

d.clear()
#  deque([])

d.extendleft('abc')
#  deque(['c', 'b', 'a', 1, 1, 2, 0])

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

#----------------------------------------------
# Compile into Deterministic Finite Automata 
# Time Compleixyt O(N)
#
# Add sample of string above the raw string matches
# sample="    -123456-And thern som juck and the end"
re_pattern = (
  r'^\W*?'
  r'(?P<sign>[-+]?)'
  r'(?P<dig>\d+)'
)
rec_pattern = re.compile(re_pattern, re.VERBOSE)
match = rec_pattern.search(raw_log)
  if match is not None:
    match.group('sign')
    match.group('dig')
    print(f"{sign} {dig}")
  else:
    print("No match")

#
# match()    - match beginning of string
# search()   - match all of string
# findall()  - return all as list
# finditer() - return all as iter
#
# findall:
#   (\d)     : one digit
#   \2       : second group of (\d)
#  ((\d)\2*) : outer bracket defines the scope of the first group
#
#   re.findall(
#      r'((\d)\2*)', 
#      '11221'
#   )
#     
#   [('11', '1'), ('22', '2'), ('1', '1')]
#
#------------------
#
# Non Greedy:  
#    *?
#    +?
#    ??
#    {m,n}?
#
#------------------
# Non-capturing and Named Groups
#
# Extension Notation: (?...)    ** char after (? determins meaning
# 
# lookahead:           (?=...)
# negetive lookahead:  (?!...)
# look behind:         (?<=...)
# negetive look behind (?<!...)
# Name non-capturing:  (?:...)
# Name capturing:      (?P<sign>pattern)
# Seen non-capturing:  (?P=<sign>)   <-- A backref to Named group
# Comment ignored:     (?#...)
#
# Ternary pattern:(?(id/name)yes-pattern|no-pattern)
#   if groups id or name exsit, try match: yes-pattern
#   else   try match: no-pattern
#
# Inline Modifiers: (?aiLmsux)
#                   (?aiLmsux-imsx:...)
#  APPLYS TO THE WHOLE PATTER (can't be disabled)
#  ONLY APPLIES TO NON-CAPTUREING GROUPS
#  a = ASCII-only matching
#  i = ignore case
#  L = locale dependent  <<= DISCOURAGED
#  m = multiline
#  s = dot also match <new line>
#  u = unicode match
#  x = verbose
#
# NOTE: flags: re.I, re.L, re.M, re.S, re.U, re.VERBOSE
#  1. These are bit wise OR'ed ( | )
#  2. Are the flgags argument to re.match(), re.search(), re.sub()
#
# string = 'Head Sholders Knees and Toes, Knees and Toes'
# Named capture with Modifiers
# MATCH:  re_pat = r'(Sholders)'
# MATCH:  re_pat = r'(?P<fub>Sholders)'
# MATCH:  re_pat = r'(?i)(SHOLDERS)'
# MATCH:  re_pat = r'(?i)(?P<foo>SHOLDERS)'
# MATCH:  re_pat = r'(?i)(?P<foo>SHOLDERS)\W(?P<bar>KNEES)'
#
#
# NO MATCH: re_pat = r'(?i:P<fub>:Sholders)'
#
#------------------
a = 'Head Sholders Knees and Toes, Knees and Toes'
re_pat = r'\W+(?P<my_stuff>stuff)(?P=fed)\W'
req_pat = re.compile(re_pat)
found = req_pat.finditer(a)
for m in found:
    print(m.gropus())

# NON GREEDY: .*?
import re
html = "<html>this that thoes</html>"
print(re.match('<.*?>', s).group())
#  <html>

# NOT MATCH:  [^F]
import re
html = "<p>this that thoes</p>"
re.findall(r"<[^>]+>", html)
['<p>', '</p>']

# SUBSTITUED  re.sub
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

# ==================================================
# Python debuggger
# ==================
#
# Common pdbcommands:
#  l(ist)      - shows where we are in code 
#  n(ext)      - Next line of code
#  c(ontinue)  - Run to the next break point or finish
#  s(tep)      - step into next 
#  r(eturn)    - step over
#  b(break)    - Add a break point to a line number 
#  And python  - From here you can view the variables
#
# Many ways to use pdb
#
# 1. Start program under control of pdb, and crash
#   $ python -m pdb my_program.py
#
#  From the python shell:
#   import buggy
#   import pdb
#   my_program.crash()
#   pdb.pm()              <= Post mordom 
#
# 2. Edit Program, and add import and call pdb
#  import pdb
#
# Add this in the code where you want to see this
#  pdb.set_trace()
#
# ==================================================
