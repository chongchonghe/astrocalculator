import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='AstroCalculator',
    version='0.2.0',
    author='ChongChong He',
    author_email='chongchong.he@anu.edu.au',
    description='A locally hosted Flask application for astronomical calculations.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/chongchonghe/acap.git',
    packages=find_packages(),
    include_package_data=True,  # Includes files from MANIFEST.in
    install_requires=[
        'flask>=2.0.0',
        'sympy>=1.8',
        'astropy>=4.0',
    ],
    entry_points={
        'console_scripts': [
            'calc=astrocalculator.app:start_server',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Ensure compliance with your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
