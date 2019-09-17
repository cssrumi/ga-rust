use std::os::raw::c_longlong;
use std::slice;

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
    let mut sum = 0 as c_longlong;

    for num in numbers.iter() {
        sum += *num;
    };
//    unsafe {
//        for num in numbers.as_ref().iter() {
//            sum += num as c_longlong;
//        };
//    }

    sum
}

