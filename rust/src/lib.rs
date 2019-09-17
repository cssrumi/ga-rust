use std::os::raw::c_longlong;
use std::slice;

pub struct Individual {
    genotype: Vec<c_longlong>,
    fitness: c_longlong,
}

impl Individual {
    fn new() -> Individual {
        Individual {
            genotype: Vec::new(),
            fitness: 0
        }
    }
    fn crossover(&self, other: &Individual) -> Individual {
        let mut new_genotype = Vec::new();
        for (a, b) in self.genotype.iter().zip(other.genotype.iter()) {
            new_genotype.append((a+b)/2);
        }
        Individual{
            genotype: new_genotype,
            fitness: 0
        }
    }
}

// test functions

#[no_mangle]
pub extern "C" fn a_function_from_rust() -> i32 {
    42
}

#[no_mangle]
pub extern "C" fn sum(a: c_longlong, b: c_longlong) -> c_longlong {
    a + b
}

#[no_mangle]
pub extern "C" fn sum_array(n: *const c_longlong, len: usize) -> c_longlong {
    let numbers = unsafe {
        assert!(!n.is_null());

        slice::from_raw_parts(n, len as usize)
    };

    let sum = numbers.iter().sum();

    sum
}

