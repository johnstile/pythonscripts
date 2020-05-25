#!/usr/bin/env python
"""
Title: A sample of sorting algorithms
REF: https://medium.com/@george.seif94/a-tour-of-the-top-5-sorting-algorithms-with-python-code-43ea9aa02889
#--------------------------------------------
NOTE: Python built-in list.sort()
  => modifies in place
  => Algorithum: Timsort (hybrid merge sort and insertion sort)
  => takes a function that returns a comparable: list.sort(key=myFunc)
This program does not use that
"""

import time


def show_it(arr):
    """print formatted array,
    align numbers, to show sort changes
    :param arr: Array of int
    """
    if not isinstance(arr, list):
        return

    # Construct formatted string array
    format_arr = []
    for i in arr:
        format_arr.append(
            "{:>2}".format(i)
        )
    format_str = ', '.join(format_arr)
    print('[{}]'.format(format_str))


def time_it(func, arr):
    """
    Collect performance info about the sort method
    :param func: sort method
    :param arr: array for the method
    :return If there is a return value, return it
    """
    start_time = time.process_time()
    result = func(arr)
    end_time = time.process_time()
    print("elapsed:{}".format(end_time - start_time))
    return result


def selection_sort(arr):
    """
    Swap first element with the smallest
    Swap second elment with next smallest
    Swap third element with next smallest
    ...continue to end...
    :param list
    :return sorted list
    """
    result = arr.copy()
    for i in range(len(result)):
        cur_val = result[i]
        min_val = min(result[i:])
        min_pos = result.index(min_val)
        result[i], result[min_pos] = result[min_pos], result[i]

    return result


def bubble_sort(arr):
    """
    Step though list sequentially to the end, swaps adjacent if left is greater.
    Optimized: if no swaps in a round, the list is sorted (could save iterations)
    Worst case complexity of O(n²)
    :param list
    :return sorted list
    """
    result = arr.copy()
    continue_sorting = True
    while continue_sorting:
        swap_count = 0  # When nothing changes array is sorted
        for i in range(len(result)):
            if i < len(result) - 1:
                if result[i] > result[i + 1]:
                    swap_count += 1
                    result[i], result[i + 1] = result[i + 1], result[i]

        if swap_count == 0:
            continue_sorting = False

    return result


def inseration_sort(arr):
    """
    Compare adjacent values, swap if needed
    If swap, repeat comparison backwards, moving number lower
    :param list
    :return sorted list

    Algorithm :
     Worst complexity: n^2
     Average complexity: n^2
     Best complexity: n
     Space complexity: 1
     Method: Insertion
     Stable: Yes
     Class: Comparison sort
    """
    result = arr.copy()
    for i in range(1, len(result)):
        key = result[i]  # tmp holds current value
        j = i - 1  # get previous element
        while j >= 0 and key < arr[j]:
            # Move value forward
            result[j + 1] = result[j]
            # Step back one in the array, and repeat
            j -= 1
        # Assign key
        result[j + 1] = key
    return result


# -----------------------------
def merge_sort(arr):
    """
    Divide and Conquer, recursively
    Split array by half until you have 2 element lists
    Order the two elements
    join the elements
    :param arr:
    :return: sorted array
    """

    if len(arr) < 2:
        return arr
    else:
        halfway_index = len(arr) // 2  # Finding the halfway_index of the array
        left = arr[:halfway_index]
        right = arr[halfway_index:]

        # Continue to Break into smaller arrays
        left = merge_sort(left)  # Sorting the first half
        right = merge_sort(right)  # Sorting the second half

        # Join 2 arrays, sorting element by element
        sorted_arr = merge(left, right)
        return sorted_arr


def merge(left, right):
    len_l = len(left)
    len_r = len(right)
    il = 0
    ir = 0
    merged = []
    # Find smallest
    while il < len_l and ir < len_r:
        if left[il] <= right[ir]:
            merged.append(left[il])
            il += 1
        else:
            merged.append(right[ir])
            ir += 1
    # Sort the remaining
    while il < len_l:
        merged.append(left[il])
        il += 1
    while ir < len_r:
        merged.append(right[ir])
        ir += 1

    return merged


# -----------------------------
def quick_sort(arr):
    """
    Divide and Conquer, Recursive
    Select pivot value (lots of ways)
    , partition others left or right of pivot,
    Recursively repeat on sub arrays
    Optimized: if no swaps in a round, the list is sorted
    Worst case:  O(n^2)
    Average case:  O(nlogn
    :param list
    :return sorted list
    """
    result = arr.copy()
    quick_iter(result, 0, len(result) - 1)
    return result


def quick_iter(arr, li, ri):
    if li < ri:  # more than one item to be sorted
        # index of paritioner
        part_i = partition(arr, li, ri)
        quick_iter(arr, li, part_i - 1)
        quick_iter(arr, part_i + 1, ri)
        #show_it(arr)


def partition(arr, li, ri):
    pivot_i = get_pivot(arr, li, ri)
    pivot_v = arr[pivot_i]
    # swap left most value with pivot
    arr[li], arr[pivot_i] = arr[pivot_i], arr[li]
    # border index is li
    border_i = li
    # iterate list,
    for i in range(li, ri + 1):
        if arr[i] < pivot_v:
            # Move items less than pivot value to the left of the boarder and advance boarder
            # - swap item i with boarder value, and move baroder forward
            border_i += 1
            arr[i], arr[border_i] = arr[border_i], arr[i]
    # Place pivot value into boarder position
    arr[li], arr[border_i] = arr[border_i], arr[li]
    #show_it(arr)

    # return index of pivot
    return border_i


def get_pivot(arr, li, ri):
    mi = ri - li // 2  # // = round up
    if arr[li] < arr[ri]:
        if arr[mi] < arr[ri]:
            pivot_i = mi
        else:
            pivot_i = li
    else:
        pivot_i = ri
    return pivot_i


# -----------------------------
# Heap Sort
# Counting Sort
# Radix Sort
# Bucket Sort
# -----------------------------

if __name__ == '__main__':

    arr_unsorted = [12, 11, 13, 5, 99, 6, 42, 0]
    print("==============selection_sort==============")
    show_it(arr_unsorted)
    result = time_it(selection_sort, arr_unsorted)
    show_it(result)
    print("==============bubble_sort==============")
    show_it(arr_unsorted)
    result = time_it(bubble_sort, arr_unsorted)
    show_it(result)
    print("==============inseration_sort==============")
    show_it(arr_unsorted)
    result = time_it(inseration_sort, arr_unsorted)
    show_it(result)
    print("==============merge_sort==============")
    show_it(arr_unsorted)
    result = time_it(merge_sort, arr_unsorted)
    show_it(result)
    print("==============quick_sort==============")
    show_it(arr_unsorted)
    result = time_it(quick_sort, arr_unsorted)
    show_it(result)
