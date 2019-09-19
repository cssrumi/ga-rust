import ctypes
from ga._native import lib


def test():
    return lib.a_function_from_rust()


def sum_array(arr: list):
    return lib.sum_array(arr, len(arr))


class Individual:
    def __init__(self):
        self._pointer = lib.individual_new()

    def __del__(self):
        lib.individual_free(self._pointer)

    def __str__(self):
        ptr = lib.individual_to_string(self._pointer)
        print(ptr)
        return str(ptr)
        # try:
        #     return ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf-8')
        # finally:
        #     lib.string_free(ptr)


class TrainingData:
    def __init__(self, size=0):
        self._pointer = lib.training_data_new()
        self.size = size

    @staticmethod
    def to_float(data: list):
        new_data = []
        for value in data:
            try:
                new_data.append(float(value))
            except (TypeError, ValueError):
                return
        return new_data

    def add(self, data: list):
        data = map(TrainingData.to_float, data)
        data = filter(lambda x: len(x) == self.size, data)
        for d in data:
            lib.training_data_add(d, self._pointer)

    def __del__(self):
        lib.training_data_free(self._pointer)

    def __str__(self):
        lib.training_data_to_string(self._pointer)
