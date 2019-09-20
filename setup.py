import os
import sys

from setuptools import setup

module_path = 'ga._native'

dylib_path = 'target/i686-pc-windows-msvc/release' if os.name == 'nt' else 'target/release'
repair = True if 'PYPY' in str(sys.version).upper() and os.name == 'nt' else False


def build_native(spec):
    # build an example rust library
    build = spec.add_external_build(
        cmd=['cargo', 'build', '--release'],
        path='./rust'
    )

    spec.add_cffi_module(
        module_path=module_path,
        dylib=lambda: build.find_dylib('ga', in_path=dylib_path),
        header_filename=lambda: build.find_header('ga.h', in_path='target'),
        rtld_flags=['NOW', 'NODELETE']
    )


setup(
    name='ga',
    version='0.0.1',
    packages=['ga'],
    zip_safe=False,
    platforms='any',
    setup_requires=['milksnake'],
    install_requires=['milksnake'],
    milksnake_tasks=[
        build_native
    ]
)


def win_pypy_fix():
    module_path_list = module_path.split('.')
    module_dir = module_path_list[:len(module_path_list) - 1]
    fix_path = os.path.join(os.path.dirname(__file__), *module_dir)
    for file in os.listdir(fix_path):
        if 'None' in file:
            old_file_path = os.path.join(*module_dir, file)
            new_file = file.replace('None', '.dll')
            new_file_path = os.path.join(*module_dir, new_file)
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            os.rename(old_file_path, new_file_path)

            py_lib_file = os.path.join(*module_dir, '_native.py')
            py_lib = []
            with open(py_lib_file, 'r') as f:
                py_lib = f.readlines()
            py_lib = [line.replace(file, new_file) for line in py_lib]
            with open(py_lib_file, 'w') as f:
                f.writelines(py_lib)


if repair:
    win_pypy_fix()
