import ctypes
from ga._native import lib, ffi


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
        cdata = lib.individual_to_u8(self._pointer)
        r_str = RStr(cdata)
        return str(r_str)

    def to_rstr(self):
        cdata = lib.individual_to_u8(self._pointer)
        r_str = RStr(cdata)
        return r_str


class RStr:
    def __init__(self, cdata):
        self._ptr = cdata

    def __str__(self):
        s = ffi.string(self._ptr)
        r = s.decode("utf-8")
        return r

    def __del__(self):
        lib.string_free(self._ptr)


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
        cdata = lib.training_data_to_string(self._pointer)
        s = ffi.string(cdata)
        s = s.decode("utf-8")
        lib.string_free(cdata)
        return s
