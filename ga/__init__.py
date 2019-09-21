import ctypes
from typing import List, Optional, Union

from ga._native import lib, ffi


def test():
    return lib.a_function_from_rust()


def sum_array(arr: list):
    return lib.sum_array(arr, len(arr))


class Individual:
    def __init__(self):
        self._ptr = lib.individual_new()

    def __del__(self):
        lib.individual_free(self._ptr)

    def __str__(self):
        cdata = lib.individual_to_c_char(self._ptr)
        r_str = CStr(cdata)
        return str(r_str)

    def to_cstr(self):
        cdata = lib.individual_to_c_char(self._ptr)
        r_str = CStr(cdata)
        return r_str


class TrainingData:
    def __init__(self, data: List[list], row_size: int):
        self._row_size = row_size
        data = self.validate_data(data)
        self._ptr = lib.training_data_init(
            data, len(data), row_size
        )

    @staticmethod
    def row_to_double(row: list) -> Optional[list]:
        new_data = []
        for value in row:
            try:
                new_data.append(float(value))
            except (TypeError, ValueError):
                return None
        c_data = ffi.new("double[]", new_data)
        return c_data

    def validate_data(self, data: List[list]) -> Optional[List[List[float]]]:
        data = filter(lambda row: len(row) == self._row_size, data)
        data = map(TrainingData.row_to_double, data)
        data = filter(lambda row: row, data)
        if data:
            data = list(data)
        return data

    def add(self, data: Union[List[list], list]) -> None:
        if len(data):
            if not isinstance(data[0], list):
                data = [data]
        data = self.validate_data(data)
        print(data)
        for row in data:
            lib.training_data_add(self._ptr, row, self._row_size)

    def __del__(self):
        lib.training_data_free(self._ptr)

    def __str__(self):
        cdata = lib.training_data_to_c_char(self._ptr)
        r_str = CStr(cdata)
        return str(r_str)

    def to_cstr(self):
        cdata = lib.training_data_to_c_char(self._ptr)
        r_str = CStr(cdata)
        return r_str


class CStr:
    def __init__(self, cdata):
        self._ptr = cdata

    def __str__(self):
        s = ffi.string(self._ptr)
        r = s.decode("utf-8")
        return r

    def __del__(self):
        lib.string_free(self._ptr)
