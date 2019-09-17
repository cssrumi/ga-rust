import os

from cffi import FFI


ffi = FFI()

ffi.cdef("""
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

int32_t a_function_from_rust(void);

long long sum(long long a, long long b);

long long sum_array(const long long *n, uintptr_t len);
""")

lib = ffi.dlopen('example.dll')


a = lib.sum_array([1, 2, 3, 4])
print(a)
