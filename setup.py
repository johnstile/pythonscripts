"""
sample setuptools packager script for a flask applicaiton
- Searches a directory named 'src'
- Finds packages under src (subdirs should contain a __init__.py)
- Creates a Wheel format file
- Product location: dist/*.whl
- One would pip install this file on the web server

Build wheel:    python setup.py bdist_wheel
Install wheel:  pip install dist/*.whl 
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

install_requires = [
  "Flask>=1.1.1",
  "Flask-Cors>=3.0.8",
  "flask_redis>=0.4.0",
  "Flask-SocketIO>=4.2.1",
  "Flask-SSE>=0.2.1",
  "retrying>=1.3.3",
  "rq>=1.3.0",
  "rq-dashboard>=0.6.1",
  "pexpect>=4.7.0",
  "pykwalify>=1.7.0",
  "pyparsing>=2.4.5",
  "python-socketio>=4.4.0",
  "pyserial>=3.4",
  "PyYAML>=5.2",
  "requests>=2.22.0",
  "requests-unixsocket>=0.2.0",
] 

setup_requires = []

tests_require = [
    "boto3>=1.7.84",
    "botocore>=1.10.84",
    "moto>=1.3.6",
    "pytest>=5.4.3",
    "pytest-cov>=2.10.0",
    "pytest-mock>=3.1.1",
    "pytest-sugar>=0.9.3",
]

extras_require = {
    "dev": [
        "flake8",
        "autopep8",
        "sphinx",
    ]
    + tests_require
}

with open(os.path.join("src", "web", "README.md"), "r") as fh:
    long_description = fh.read()

setup(
    name="web",
    version="0.0.1",
    author="John Stile",
    author_email="john@stilen.com",
    description="App Bundle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["service"],
    install_requires=install_requires,
    extras_require=extras_require,
    setup_requires=setup_requires,
    tests_require=tests_require,
    package_dir={"": "src"},
    packages=find_packages("src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
