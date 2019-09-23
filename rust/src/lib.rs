extern crate rand;
extern crate rayon;

use rayon::prelude::*;
use rand::{thread_rng, Rng};
use rand::seq::SliceRandom;
use std::os::raw::{c_longlong, c_double, c_char};
use std::slice;
use std::ffi::{CString, CStr};
use std::cmp::Ordering::Equal;
use std::borrow::Borrow;
use std::ops::Deref;

pub struct Individual {
    genotype: Vec<c_double>,
    fitness: c_double,
    age: usize,
}

impl Individual {
    fn new() -> Individual {
        Individual {
            genotype: Vec::new(),
            fitness: 0.0,
            age: 0,
        }
    }
    fn random(gen_number: usize, training_data: &TrainingData) -> Individual {
        let mut rng = thread_rng();
        let mut genotype = Vec::new();
        for _ in 0..gen_number {
            let value: c_double = rng.gen();
            let gen = value * 2.0 - 1.0;
            genotype.push(gen);
        }
        let fitness = calculate_fitness(&genotype, training_data);
        Individual {
            genotype,
            fitness,
            age: 0,
        }
    }
    fn crossover(&self, other: &Individual, training_data: &TrainingData) -> Individual {
        let mut new_genotype = Vec::new();
        for (a, b) in self.genotype.iter().zip(other.genotype.iter()) {
            new_genotype.push((a + b) / 2.0);
        }
        let fitness = calculate_fitness(&new_genotype, training_data);
        Individual {
            genotype: new_genotype,
            fitness,
            age: 0,
        }
    }
    fn mutate(&self, training_data: &TrainingData) -> Individual {
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
        let fitness = calculate_fitness(&new_genotype, training_data);
        Individual {
            genotype: new_genotype,
            fitness,
            age: 0,
        }
    }
    fn predict_value(&self, data: &Vec<f64>) -> f64 {
        let mut result = 0.0;
        for (gen, value) in self.genotype.iter().zip(data.iter()) {
            result += gen * value;
        }
        result
    }
    fn dup(&self) -> Individual {
        Individual {
            genotype: self.genotype.to_owned(),
            fitness: self.fitness,
            age: self.age,
        }
    }
}
// TODO Fix String representation of this function
impl ToString for Individual {
    fn to_string(&self) -> String {
        let mut as_string = String::from("<Individual: \n<genotype: [");
        if self.genotype.len() > 0 {
            for value in self.genotype.iter() {
                as_string += &value.to_string();
                as_string += &", ";
            }
            as_string.pop();
            as_string.pop();
        }
        as_string += &"]>";
        as_string += &"\n<fitness: ";
        as_string += &self.fitness.to_string();
        as_string += &">";
        as_string += &"\n<age: ";
        as_string += &self.age.to_string();
        as_string += &">";
        as_string += &"\n>";
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
    data: Vec<Vec<c_double>>,
    genotype_size: usize,
}

impl TrainingData {
    fn new() -> TrainingData {
        TrainingData {
            data: Vec::new(),
            genotype_size: 0,
        }
    }
    fn from_vec(data: Vec<Vec<c_double>>) -> TrainingData {
        let genotype_size;
        if data.len() > 0 {
            // training row size have additional value to predict
            genotype_size = data[0].len() - 1;
        } else {
            genotype_size = 0;
        }
        TrainingData {
            data,
            genotype_size,
        }
    }
    fn add_row(&mut self, row: Vec<c_double>) {
        if self.genotype_size == 0 {
            // training row size have additional value to predict
            self.genotype_size = row.len() - 1;
        }
        self.data.push(row);
    }
}

impl ToString for TrainingData {
    fn to_string(&self) -> String {
        let mut as_string = String::from("<TrainingData: <data: [");
        if self.data.len() > 0 {
            for array in self.data.iter() {
                as_string += &"[";
                if array.len() > 0 {
                    for value in array.iter() {
                        as_string += &value.to_string();
                        as_string += &", ";
                    }
                    // remove last ", "
                    as_string.pop();
                    as_string.pop();
                }
                as_string += &"], "
            }
            // remove last ", "
            as_string.pop();
            as_string.pop();
        }
        as_string += &"]>>";
        as_string
    }
}

// External functions for TrainingData

#[no_mangle]
pub extern fn training_data_new() -> *mut TrainingData {
    let obj = TrainingData::new();
    Box::into_raw(Box::new(obj))
}

#[no_mangle]
pub extern fn training_data_init(data_ptr: *const *const c_double, data_len: usize,
                                 row_len: usize) -> *mut TrainingData {
    assert!(!data_ptr.is_null());
    let data_slice = unsafe { slice::from_raw_parts(data_ptr, data_len) };
    let mut data = Vec::new();
    for row_ptr in data_slice.iter() {
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
    unsafe { (*training_data).add_row(data) };
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
    training_data: TrainingData,
    header: Vec<String>,
    max_children_size: usize,
    genotype_size: usize,
    crossover_chance: c_double,
    mutation_chance: c_double,
    max_age: usize,
}

impl Population {
    // TODO Add function that create instance of Population with empty training data

    // TODO change this function name to from_trainig_data
    fn new(training_data: TrainingData, initial_population_size: usize,
           max_children_size: usize) -> Population {
        let genotype_size = training_data.genotype_size;
        let initial_population = Population::random_individuals(
            initial_population_size, genotype_size, &training_data,
        );
        Population {
            individuals: initial_population,
            best: Individual::new(),
            training_data,
            header: Vec::new(),
            max_children_size,
            genotype_size,
            crossover_chance: 0.5,
            mutation_chance: 0.5,
            max_age: 7,
        }
    }
    fn random_individuals(init_size: usize, genotype_size: usize,
                          training_data: &TrainingData) -> Vec<Individual> {
        let individuals = (0..init_size).into_par_iter()
            .map(|_| Individual::random(genotype_size, training_data))
            .collect();
        individuals
    }
    fn increment_age(&mut self) {
        self.individuals.par_iter_mut().for_each(|i| i.age += 1);
    }
    fn decrement_population(&mut self) {
        self.individuals = self.individuals
            .par_iter()
            .filter(|i| i.age < self.max_age)
            .collect::<Vec<&Individual>>()
            .into_par_iter()
            .map(Individual::dup)
            .collect();
    }
    fn evolve_by_rank(&mut self) {
        // Reverse sort because the bigger fitness is the worse
        self.individuals.par_sort_by(
            |a, b| b.fitness
                .partial_cmp(&a.fitness)
                .unwrap_or(Equal));
        let population_size = self.individuals.len();
        let rank_sum = (population_size * (population_size + 1) / 2) as f64;
        let rank_vec: Vec<f64> = (1..population_size + 1)
            .into_par_iter()
            .map(|i| {
//                let i = i as u32;
                let rv: u32 = (1..i as u32 + 1).into_iter().sum();
                let rv = rv as f64 / rank_sum;
                rv
            })
            .collect();
        // generate new generation of Individuals
        let mut children: Vec<Individual> = (0..self.max_children_size)
            .into_par_iter()
            .filter(|_| {
                let mut rng = thread_rng();
                let crossover: f64 = rng.gen();
                crossover <= self.crossover_chance
            })
            .map(|_| {
                let mother = &self.individuals[
                    get_parent_id(population_size, &rank_vec)];
                let father = &self.individuals[
                    get_parent_id(population_size, &rank_vec)];

                mother.crossover(&father, &self.training_data)
            }).collect();
        // generate mutated individuals
        let mut mutated: Vec<Individual> = (0..self.max_children_size)
            .into_par_iter()
            .filter(|_| {
                let mut rng = thread_rng();
                let mutate: f64 = rng.gen();
                mutate <= self.mutation_chance
            })
            .map(|_| {
                let to_mutate = &self.individuals[
                    get_parent_id(population_size, &rank_vec)];
                to_mutate.mutate(&self.training_data)
            })
            .collect();
        self.increment_age();
        self.decrement_population();
        // Add both to population
        self.individuals.append(&mut children);
        self.individuals.append(&mut mutated);
    }
}
// TODO Fix this function and add header
impl ToString for Population {
    fn to_string(&self) -> String{
        let mut as_string = String::from("<Population: \n<Individuals :[");
        if self.individuals.len() > 0 {
            for value in self.individuals.iter() {
                as_string += &value.to_string();
                as_string += &", ";
            }
            as_string.pop();
            as_string.pop();
        }
        as_string += &"]>,\n<Best: ";
        as_string += &self.best.to_string();
        as_string += &">,\n";
        as_string += &self.training_data.to_string();
        as_string += &"\n>";
        as_string
    }
}

// External functions for Population

// TODO Add External function from_training_data

// TODO Rewrite this function to one that don't require training data and create empty training data
#[no_mangle]
pub extern "C" fn population_new(training_data_ptr: *mut TrainingData,
                                 initial_population_size: usize,
                                 max_children_size: usize) -> *mut Population {
    assert!(!training_data_ptr.is_null());
    let mut training_data = unsafe { Box::from_raw(training_data_ptr) };
    Box::into_raw(Box::new(
        Population::new(*training_data, initial_population_size, max_children_size)
    ))
}

// TODO Add External function create_training_data that create td and pass it to the population ptr

// TODO Add External functions for setting mutation and crossover chances

#[no_mangle]
pub extern "C" fn population_free(population: *mut Population) {
    if population.is_null() { return; }
    unsafe { Box::from_raw(population); }
}

#[no_mangle]
pub extern "C" fn population_evolve(population: *mut Population) {
    if population.is_null() { return; }
    unsafe { (*population).evolve_by_rank() };
}

#[no_mangle]
pub extern "C" fn population_set_header(population: *mut Population,
                                        ptr: *const *const c_char, len: usize) {
    assert!(!ptr.is_null());
    assert!(!population.is_null());
    let header_slice = unsafe { slice::from_raw_parts(ptr, len) };
    let mut header = Vec::new();
    for element in header_slice.iter() {
        let c_str = unsafe { CStr::from_ptr(*element) };
        let string = String::from(c_str.to_str().unwrap());
        header.push(string)
    }
    unsafe { (*population).header = header };
}

#[no_mangle]
pub extern "C" fn population_to_c_char(population: *mut Population) -> *const c_char {
    assert!(!population.is_null());
    struct_to_c_char(population)
}

#[no_mangle]
pub extern "C" fn population_data_to_u8(population: *mut Population) -> *const u8 {
    assert!(!population.is_null());
    struct_to_u8(population)
}

// Other useful tools

fn calculate_fitness(genotype: &Vec<c_double>, training_data: &TrainingData) -> c_double {
    let index_of_value = genotype.len();
    let mut final_fitness: c_double = 0.0;
    for row in training_data.data.iter() {
        let mut fitness: c_double = 0.0;
        for (gen, col) in genotype.iter().zip(row.iter()) {
            fitness += gen * col;
        }
        fitness = row[index_of_value] - fitness;
        final_fitness += fitness.abs();
    }
    final_fitness
}

pub fn get_parent_id(population_size: usize, rank_vec: &Vec<f64>) -> usize {
    let mut rng = thread_rng();
    let value: f64 = rng.gen();
    for (i, rank) in rank_vec.iter().enumerate() {
        if value > *rank {
            return i;
        }
    }
    population_size - 1
}

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
