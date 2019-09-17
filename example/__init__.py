from example._native import ffi, lib


def test():
    return lib.a_function_from_rust()


def sum_array(arr: list):
    return lib.sum_array(arr, len(arr))
