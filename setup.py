from setuptools import setup, find_packages

version = '0.0.11'

setup(
    name='gdsync',
    version=version,
    description='Google Drive Synchronizer',
    long_description=open("README.rst").read(),
    author='Masato Bito',
    author_email='bito_m@uuum.jp',
    url='https://github.com/uuum/gdsync',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=['click', 'google-api-python-client', 'python-dateutil'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['gdsync=gdsync.cli.cli:main']
    },
)
