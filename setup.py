import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='AstroCalculator',
    version='0.3.0',
    description='AstroCalculator, a Calculator for Astronomers and Physicists',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/chongchonghe/acap.git',
    author='Chong-Chong He',
    author_email='chongchong.he@anu.edu.au',
    license="MIT",
    # packages=find_packages(),
    packages=["calc"],
    # entry_points={'console_scripts': ['calc=calc:main']},
    entry_points={'console_scripts': ['calc=calc.__init__:main_interactive', 'calceval=calc.__init__:main_non_interactive', 
                                      'calcevalfile=calc.__init__:main_eval_file']},
    install_requires=['sympy>=1.6', 'astropy>=4.0'],
)
