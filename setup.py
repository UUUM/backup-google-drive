from setuptools import setup

try:
    import pypandoc

    def read_md(file):
        return pypandoc.convert(file, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")

    def read_md(file):
        return open(file, 'r').read()


setup(
    name='gdsync',
    version='0.0.1',
    description='Google Drive Synchronizer',
    author='Masato Bito',
    author_email='bito_m@uuum.jp',
    url='https://github.com/uuum/gdsync',
    license='MIT',
    long_description=read_md('README.md'),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
