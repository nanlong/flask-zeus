from distutils.core import setup
from setuptools import find_packages

PACKAGE = "flask_zeus"
NAME = "flask-zeus"
DESCRIPTION = ""
AUTHOR = "Jeff"
AUTHOR_EMAIL = "fei.code@gmail.com"
URL = "https://github.com/nanlong/flask_zeus"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=['flask_zeus']
)