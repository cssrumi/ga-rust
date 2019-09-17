from setuptools import setup

module_path = 'example._native'


def build_native(spec):
    # build an example rust library
    build = spec.add_external_build(
        cmd=['cargo', 'build', '--release'],
        path='./rust'
    )

    spec.add_cffi_module(
        module_path=module_path,
        dylib=lambda: build.find_dylib('example', in_path='target/release'),
        header_filename=lambda: build.find_header('example.h', in_path='target'),
        rtld_flags=['NOW', 'NODELETE']
    )


setup(
    name='example',
    version='0.0.1',
    packages=['example'],
    zip_safe=False,
    platforms='any',
    setup_requires=['milksnake'],
    install_requires=['milksnake'],
    milksnake_tasks=[
        build_native
    ]
)

libs = ['dll', 'so', 'dylib']


def pypy_fix():
    import os
    from shutil import copyfile

    module_path_split = module_path.split('.')
    header_file = module_path_split[0] + '.h'

    target_dir = os.path.join(os.path.dirname(__file__), 'rust', 'target')
    release_dir = os.path.join(target_dir, 'release')
    module_dir = os.path.join(os.path.dirname(__file__), module_path_split[0])
    lib_file = ''
    for filename in os.listdir(release_dir):
        for lib in libs:
            if filename.endswith(lib):
                copyfile(
                    os.path.join(release_dir, filename),
                    os.path.join(module_dir, filename)
                )
                lib_file = filename
    copyfile(
        os.path.join(target_dir, header_file),
        os.path.join(module_dir, header_file)
    )
    lib_declaration_file = os.path.join(module_dir, module_path_split[1]) + '.py'
    final_file = []
    with open(lib_declaration_file, 'r') as native_file:
        for line in native_file.readlines():
            if 'lib = ffi.dlopen' in line:
                line = "lib = ffi.dlopen(os.path.join(os.path.dirname(__file__), '{}'), 0)".format(lib_file) + '\n'
            final_file.append(line)
    with open(lib_declaration_file, 'w+') as file_to_fix:
        file_to_fix.writelines(final_file)

    print('PYPY FIXED')


try:
    from example._native__ffi import ffi
except OSError:
    pypy_fix()
except ModuleNotFoundError:
    pass
