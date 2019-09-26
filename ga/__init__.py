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


class Population:
    def __init__(self, training_data: List[list],
                 training_data_row_size: int,
                 initial_population_size: int = 200,
                 max_age: int = 7,
                 max_children_size: int = 50,
                 mutation_chance: float = 0.9,
                 crossover_chance: float = 0.8,
                 header: Optional[List[str]] = None):
        # initialization
        self.__population_ptr = None
        self.__training_data = None
        self.__training_data_row_size = None
        # TODO Add TrainingDataRowSize setter
        self.training_data_row_size = training_data_row_size
        self.__initial_population_size = 200
        # TODO Add InitialPopulationSize setter
        self.initial_population_size = initial_population_size
        self.__max_age = 7
        self.max_age = max_age
        self.__max_children_size = max_children_size
        self.__mutation_chance = mutation_chance
        self.__crossover_chance = crossover_chance
        self.__header = header

        # Validation of training data
        self.training_data = training_data

        self.create_population_from_training_data()

    def create_population_from_training_data(self):
        if self.__population_ptr:
            lib.population_free(self.__population_ptr)
        cdata = list(map(Population.row_to_c_double, self.training_data))
        training_data_ptr = lib.training_data_init(
            cdata, len(cdata), self.training_data_row_size
        )

        self.__population_ptr = lib.population_from_training_data(
            training_data_ptr,
            self.initial_population_size,
            self.max_children_size
        )


    @property
    def training_data(self):
        return self.__training_data

    @training_data.setter
    def training_data(self, data: List[list]):
        if not self.training_data_row_size or self.training_data_row_size < 0:
            print("Invalid Training Data row size")
            return
        if not self.__training_data:
            data = filter(lambda row: len(row) == self.training_data_row_size, data)
            data = map(Population.row_to_float, data)
            data = filter(lambda row: row, data)
            self.__training_data = list(data) if data else None
        else:
            print("Training Data is immutable")

    @property
    def training_data_row_size(self):
        return self.__training_data_row_size

    @property
    def initial_population_size(self):
        return self.__initial_population_size

    @property
    def max_age(self):
        return self.__max_age

    @max_age.setter
    def max_age(self, value: int):
        try:
            value = int(value)
        except (TypeError, ValueError):
            print("Unable to set value of max_age")
        if value > 0:
            if self.__population_ptr:
                lib.population_set_max_age(self.__population_ptr, value)
                self.__max_age = value
            else:
                raise ValueError("Invalid pointer to Population Struct")
        else:
            print("The minimum value of max_age is 1")

    @property
    def max_children_size(self):
        return self.__max_children_size

    @max_children_size.setter
    def max_children_size(self, value: int):
        try:
            value = int(value)
        except (TypeError, ValueError):
            print("Unable to set value of max_children_size")
        if value > 0:
            if self.__population_ptr:
                lib.population_set_max_children_size(self.__population_ptr, value)
                self.__max_children_size = value
            else:
                raise ValueError("Invalid pointer to Population Struct")
        else:
            print("The minimum value of max_children_size is 1")

    @property
    def mutation_chance(self):
        return self.__mutation_chance

    @mutation_chance.setter
    def mutation_chance(self, value: float):
        try:
            value = float(value)
        except (TypeError, ValueError):
            print("Unable to set value of mutation_chance")
        if value > 0.0:
            if self.__population_ptr:
                lib.population_set_mutation_chance(self.__population_ptr, value)
            else:
                raise ValueError("Invalid pointer to Population Struct")

    @property
    def crossover_chance(self):
        return self.__crossover_chance

    @crossover_chance.setter
    def crossover_chance(self, value: float):
        try:
            value = float(value)
        except (TypeError, ValueError):
            print("Unable to set value of mutation_chance")
        if value > 0.0:
            if self.__population_ptr:
                lib.population_set_crossover_chance(self.__population_ptr, value)
            else:
                raise ValueError("Invalid pointer to Population Struct")

    @property
    def header(self):
        return self.__header

    @header.setter
    def header(self, new_header: List[str]):
        if isinstance(new_header, str):
            try:
                new_header = [str(s) for s in new_header]
            except (TypeError, ValueError) as e:
                print(e)
            new_header_len = len(new_header)
            c_str_list = [ffi.new("char *", s) for s in new_header]
            new_c_header = ffi.new("char[]", *c_str_list)
            if self.__population_ptr:
                if self.training_data_row_size:
                    if self.training_data_row_size == new_header_len:
                        lib.population_set_header(self.__population_ptr, new_c_header)
                        self.__header = new_header
                else:
                    lib.population_set_header(self.__population_ptr, new_c_header)
                    self.__header = new_header
            else:
                raise ValueError("Invalid pointer to Population Struct")
        else:
            print("Unable to set value of header")

    def evolve(self):
        lib.population_evolve(self.__population_ptr)

    @staticmethod
    def row_to_float(row: list) -> Optional[List[float]]:
        new_data = []
        for value in row:
            try:
                new_data.append(float(value))
            except (TypeError, ValueError):
                return None
        return new_data

    @staticmethod
    def row_to_c_double(row: List[float]) -> list:
        c_data = ffi.new("double[]", row)
        return c_data

    def __del__(self):
        lib.population_free(self.__population_ptr)

    def __str__(self):
        cdata = lib.population_to_c_char(self.__population_ptr)
        r_str = CStr(cdata)
        return str(r_str)

    def to_cstr(self):
        cdata = lib.population_to_c_char(self.__population_ptr)
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
