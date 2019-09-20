import ctypes
import time

from ga import TrainingData, Individual


def test_str():
    i = Individual()
    r = i.to_rstr()

    ptr = r._ptr

    print(r)

    r.__del__()
    time.sleep(1)

    # empty
    print(r)
    # error
    print(ptr)

#
# t = TrainingData(size=2)
#
# arr_or_arr = [
#     [1, 2],
#     [2, 4],
#     [4.4, 2]
# ]
#
# t.add(arr_or_arr)
# print(t)
