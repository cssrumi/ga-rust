extern crate rand;
//extern crate libc;

use rand::{thread_rng, Rng};
use rand::seq::SliceRandom;
use std::os::raw::{c_longlong, c_double, c_char};
use std::slice;
use std::ffi::CString;

pub struct Individual {
    genotype: Vec<c_double>,
    fitness: c_double,
}

impl Individual {
    fn new() -> Individual {
        Individual {
            genotype: Vec::new(),
            fitness: 0.0,
        }
    }
    fn crossover(&self, other: &Individual) -> Individual {
        let mut new_genotype = Vec::new();
        for (a, b) in self.genotype.iter().zip(other.genotype.iter()) {
            new_genotype.push((a + b) / 2.0);
        }
        Individual {
            genotype: new_genotype,
            fitness: 0.0,
        }
    }
    fn mutate(&self) -> Individual {
        let mut rng = thread_rng();
        let mut new_genotype = vec![0 as c_double; self.genotype.len()];
        let shuffled_indexes: Vec<usize> = (0..self.genotype.len()).collect();
        let shuffled_indexes = copy_shuffle(&shuffled_indexes);
        for (iteration, index) in (0..self.genotype.len()).zip(shuffled_indexes) {
            if iteration % 2 == 0 {
                new_genotype[index] = self.genotype[index];
            } else {
                // random number between -1 to 1
                // rng.gen() generate value between 0 to 1
                let new_value: c_double = rng.gen();
                let new_value = new_value * 2.0 - 1.0;
                new_genotype[index] = new_value;
            }
        }
        Individual {
            genotype: new_genotype,
            fitness: 0.0,
        }
    }
    fn predict_value(&self, data: &Vec<f64>) -> f64 {
        let mut result = 0.0;
        for (gen, value) in self.genotype.iter().zip(data.iter()) {
            result += gen * value;
        }
        result
    }
}

impl ToString for Individual {
    fn to_string(&self) -> String {
        let mut as_string = String::from("<Individual: <genotype: [");
        for value in self.genotype.iter() {
            as_string += &value.to_string();
            as_string += &", ";
        }
        as_string += &"]>>";
        as_string
    }
}

// External function for Individual

#[no_mangle]
pub extern fn individual_new() -> *mut Individual {
    Box::into_raw(Box::new(Individual::new()))
}

#[no_mangle]
pub extern fn individual_free(ptr: *mut Individual) {
    if ptr.is_null() { return; }
    unsafe { Box::from_raw(ptr); }
}

#[no_mangle]
pub extern "C" fn individual_to_c_char(individual: *mut Individual) -> *const c_char {
    assert!(!individual.is_null());
    struct_to_c_char(individual)
}

#[no_mangle]
pub extern "C" fn individual_to_u8(individual: *mut Individual) -> *const u8 {
    assert!(!individual.is_null());
    struct_to_u8(individual)
}

// TrainingData

pub struct TrainingData {
    data: Vec<Vec<c_double>>
}

impl TrainingData {
    fn new() -> TrainingData {
        TrainingData {
            data: Vec::new(),
        }
    }
    fn from_vec(data: Vec<Vec<c_double>>) -> TrainingData {
        TrainingData {
            data
        }
    }
    fn add_data(&mut self, data: Vec<f64>) {
        self.data.push(data);
    }
}

impl ToString for TrainingData {
    fn to_string(&self) -> String {
        let mut as_string = String::from("<TrainingData: <data: [");
        for array in self.data.iter() {
            as_string += &"[";
            for value in array.iter() {
                as_string += &value.to_string();
                as_string += &", ";
            }
            as_string += &"], "
        }
        as_string += &"]>>";
        as_string
    }
}

// External functions for TrainingData

#[no_mangle]
pub extern fn training_data_new() -> *mut TrainingData {
    let mut obj = TrainingData::new();
    Box::into_raw(Box::new(obj))
}

#[no_mangle]
pub extern fn training_data_init(data_ptr: *const *const c_double, data_len: usize,
                                 row_len: usize) -> *mut TrainingData {
    assert!(!data_ptr.is_null());
    let data_slice = unsafe { slice::from_raw_parts(data_ptr, data_len) };
    let mut data = Vec::new();
    for (row_ptr) in data_slice.iter() {
        let row = unsafe { slice::from_raw_parts(*row_ptr, row_len) };
        let row = row.to_vec();
        data.push(row);
    }
    let obj = TrainingData::from_vec(data);
    Box::into_raw(Box::new(obj))
}

#[no_mangle]
pub extern "C" fn training_data_free(ptr: *mut TrainingData) {
    if ptr.is_null() { return; }
    unsafe { Box::from_raw(ptr); }
}

#[no_mangle]
pub extern "C" fn training_data_add(training_data: *mut TrainingData,
                                    ptr: *const c_double, len: usize) {
    assert!(!ptr.is_null());
    assert!(!training_data.is_null());
    let data_slice = unsafe { slice::from_raw_parts(ptr, len) };
    let data = data_slice.to_vec();
    // Be aware that size validation has to be done in Python Lib.
    unsafe { (*training_data).add_data(data) };
}

#[no_mangle]
pub extern "C" fn training_data_to_c_char(training_data: *mut TrainingData) -> *const c_char {
    assert!(!training_data.is_null());
    struct_to_c_char(training_data)
}

#[no_mangle]
pub extern "C" fn training_data_to_u8(training_data: *mut TrainingData) -> *const u8 {
    assert!(!training_data.is_null());
    struct_to_u8(training_data)
}

// Population

pub struct Population {
    individuals: Vec<Individual>,
    best: Individual,
    training_data: Vec<Vec<f64>>,
}

// External functions for Population

// Other useful tools

pub fn copy_shuffle<T: Clone>(vec: &Vec<T>) -> Vec<T> {
    let mut vec = vec.clone();
    vec.shuffle(&mut thread_rng());
    vec
}

pub fn struct_to_c_char<T: ToString>(ptr: *mut T) -> *const c_char {
    let s = unsafe { (*ptr).to_string() };
    let c_str = CString::new(s).unwrap();
    let p = c_str.as_ptr();
    std::mem::forget(c_str);
    p
}
pub fn struct_to_u8<T: ToString>(ptr: *mut T) -> *const u8 {
    let string = unsafe { (*ptr).to_string() } + &"\0";
    let str_slice = &string[..];
    let result = str_slice.as_ptr();
    std::mem::forget(string);
    result
}

// Other external tools

#[no_mangle]
pub extern "C" fn string_free(s: *mut c_char) {
    unsafe {
        if s.is_null() { return; }
        CString::from_raw(s)
    };
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
pub extern "C" fn sum_array(ptr: *const c_longlong, len: usize) -> c_longlong {
    assert!(!ptr.is_null());
    let array = unsafe { slice::from_raw_parts(ptr, len) };
    array.iter().sum()
}
