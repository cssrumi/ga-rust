import json
import logging
from typing import List, Optional, Union

from ga._native import lib, ffi


class Individual:
    def __init__(self, ptr=None, logger: logging.Logger = logging.getLogger()):
        self.logger = logger
        if ptr:
            self._ptr = ptr
            self.logger.debug('{} created from Pointer'.format(__class__.__name__))
        else:
            self._ptr = lib.individual_new()
            self.logger.debug('{} created'.format(__class__.__name__))

    def __eq__(self, other: 'Individual'):
        if self._ptr and other._ptr:
            if lib.individual_eq_individual(self._ptr, other._ptr):
                return True
            return False
        else:
            raise ValueError("Invalid pointer to {}".format(__class__))

    @property
    def fitness(self):
        if self._ptr:
            return lib.individual_get_fitness(self._ptr)
        return 0

    @staticmethod
    def from_json(json_str: str) -> 'Individual':
        c_str = ffi.new("char []", json_str.encode('UTF-8'))
        ptr = lib.individual_from_json(c_str, len(json_str))
        return Individual(ptr)

    def to_json(self) -> dict:
        json_str = str(self)
        return json.loads(json_str)

    def to_cstr(self):
        cdata = lib.individual_to_c_char(self._ptr)
        r_str = CStr(cdata)
        return r_str

    def __del__(self):
        lib.individual_free(self._ptr)
        self.logger.debug('{} destroyed'.format(self.__class__.__name__))

    def __str__(self):
        cdata = lib.individual_to_c_char(self._ptr)
        r_str = CStr(cdata)
        return str(r_str)


class Population:
    """
    Last column of training_data must be a result(to predict) value
    """

    def __init__(self, training_data: List[list],
                 training_data_row_size: int,
                 initial_population_size: int = 200,
                 max_age: int = 7,
                 max_children_size: int = 50,
                 mutation_chance: float = 0.9,
                 crossover_chance: float = 0.8,
                 header: Optional[List[str]] = None,
                 logger: logging.Logger = logging.getLogger()):
        # initialization
        self.logger = logger
        self.__population_ptr = None
        self.__training_data = None
        self.__training_data_row_size = training_data_row_size
        self.initial_population_size = initial_population_size
        self.max_children_size = max_children_size

        # Validation of training data
        self.training_data = training_data

        # Create Population obj
        self.create_population_from_training_data()

        # Set rest of values
        self.max_age = max_age
        self.mutation_chance = mutation_chance
        self.crossover_chance = crossover_chance
        self.header = header

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
        self.logger.debug('{} instantiated'.format(self.__class__.__name__))

    def evolve(self):
        lib.population_evolve(self.__population_ptr)

    def get_best(self) -> Individual:
        i_ptr = lib.population_get_best(self.__population_ptr)
        return Individual(i_ptr)

    def add_individual(self, individual: Individual):
        lib.population_add_individual(self.__population_ptr, individual._ptr)

    def to_cstr(self):
        cdata = lib.population_to_c_char(self.__population_ptr)
        r_str = CStr(cdata)
        return r_str

    def __del__(self):
        lib.population_free(self.__population_ptr)
        self.logger.debug('{} destroyed'.format(self.__class__.__name__))

    def __str__(self):
        cdata = lib.population_to_c_char(self.__population_ptr)
        r_str = CStr(cdata)
        return str(r_str)

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

    def _setter(self, attr: str, value: object, cast: callable, lib_function: callable,
                minimal: Optional[Union[int, float]] = None):
        hidden_attr = '_{}__{}'.format(__class__.__name__, attr)
        try:
            value = cast(value)
        except (TypeError, ValueError):
            self.logger.warning("Unable to cast value of {} to {}".format(attr, cast.__name__))
            return
        if isinstance(cast, (int, float)):
            if value > 0:
                if self.__population_ptr:
                    if lib_function:
                        lib_function(self.__population_ptr, value)
                    setattr(self, hidden_attr, value)
                    self.__initial_population_size = value
                elif not hasattr(self, hidden_attr):
                    setattr(self, hidden_attr, value)
                else:
                    raise ValueError("Invalid pointer to {}".format(__class__))
            else:
                self.logger.warning("Unable to change value. The minimum value of {} is {}".format(attr, minimal))
        else:
            if self.__population_ptr:
                lib_function(self.__population_ptr, value)
                setattr(self, hidden_attr, value)
                self.__initial_population_size = value
            elif not hasattr(self, hidden_attr):
                setattr(self, hidden_attr, value)
            else:
                raise ValueError("Invalid pointer to {}".format(__class__))

    @property
    def training_data(self):
        return self.__training_data

    @training_data.setter
    def training_data(self, data: List[list]):
        if not self.training_data_row_size or self.training_data_row_size < 2:
            self.logger.warning("Invalid Training Data row size")
            return
        if not self.__training_data:
            data = filter(lambda row: len(row) == self.training_data_row_size, data)
            data = map(Population.row_to_float, data)
            data = filter(lambda row: row, data)
            self.__training_data = list(data) if data else None
        else:
            self.logger.warning("Training Data is immutable")

    @property
    def training_data_row_size(self):
        return self.__training_data_row_size

    @property
    def initial_population_size(self):
        return self.__initial_population_size

    @initial_population_size.setter
    def initial_population_size(self, value):
        self._setter('initial_population_size', value, int, None, minimal=1)

    @property
    def max_age(self):
        return self.__max_age

    @max_age.setter
    def max_age(self, value: int):
        self._setter('max_age', value, int, lib.population_set_max_age, 1)

    @property
    def max_children_size(self):
        return self.__max_children_size

    @max_children_size.setter
    def max_children_size(self, value: int):
        self._setter('max_children_size', value, int, lib.population_set_max_children_size, 1)

    @property
    def mutation_chance(self):
        return self.__mutation_chance

    @mutation_chance.setter
    def mutation_chance(self, value: float):
        self._setter('mutation_chance', value, float, lib.population_set_mutation_chance, 0.0)

    @property
    def crossover_chance(self):
        return self.__crossover_chance

    @crossover_chance.setter
    def crossover_chance(self, value: float):
        self._setter('mutation_chance', value, float, lib.population_set_crossover_chance, 0.0)

    @property
    def header(self):
        return self.__header

    @header.setter
    def header(self, new_header: List[str]):
        if isinstance(new_header, str):
            try:
                new_header = [str(s) for s in new_header]
            except (TypeError, ValueError) as e:
                self.logger.warning(e)
            new_header_len = len(new_header)
            c_str_list = [ffi.new("char *", bytes(s)) for s in new_header]
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
            self.logger.warning("Unable to set value of header")


class CStr:
    def __init__(self, cdata):
        self._ptr = cdata

    def __str__(self):
        s = ffi.string(self._ptr)
        r = s.decode("utf-8")
        return r

    def __del__(self):
        lib.string_free(self._ptr)
