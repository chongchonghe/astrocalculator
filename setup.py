from setuptools import setup, find_packages

setup(
    name='acap',
    version='0.2.0',
    url='https://github.com/chongchonghe/acap.git',
    author='Chong-Chong He',
    author_email='che1234@umd.edu',
    description='ACAP, an Awesome Calculator for Astronomers and Physicists.',
    packages=find_packages(),
    scripts=['acap'],
    install_requires=['sympy', 'astropy'],
)
