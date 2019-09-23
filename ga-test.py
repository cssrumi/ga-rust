import ctypes
import time

from ga import TrainingData, Individual, Population


def test_str():
    i = Individual()
    print(i)
    r = i.to_cstr()
    print(r)
    #
    # ptr = r._ptr
    # print(ptr)
    # r.__del__()
    # time.sleep(1)
    # 'empty'
    # print(r)
    # 'error'
    # print(ptr)
    # from ga import ffi
    # s = ffi.string(ptr)
    # print(s)


def test_training_data():
    arr_or_arr = [
        [1, 2],
        [2, 4],
        [4.4, 2]
    ]
    td = TrainingData(arr_or_arr, 2)
    print(td)
    new_data = [3, '4']
    td.add(new_data)
    print(td)


def test_population():
    arr_or_arr = [
        [1, 2],
        [2, 4],
        [4.4, 2]
    ]
    td = TrainingData(arr_or_arr, 2)
    new_data = [3, '4']
    # td.add(new_data)
    td.add(new_data)
    print(td)

    p = Population(td, 4, 10)
    p.evolve()
    print(p)


def test():
    print(test_str.__name__)
    test_str()
    print('END OF', test_str.__name__)

    print(test_training_data.__name__)
    test_training_data()
    print('END OF', test_training_data.__name__)

    print(test_population.__name__)
    test_population()
    print('END OF', test_population.__name__)


test()
