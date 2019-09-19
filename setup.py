from setuptools import setup

module_path = 'ga._native'


def build_native(spec):
    # build an example rust library
    build = spec.add_external_build(
        cmd=['cargo', 'build', '--release'],
        path='./rust'
    )

    spec.add_cffi_module(
        module_path=module_path,
        dylib=lambda: build.find_dylib('ga', in_path='target/release'),
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
