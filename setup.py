#!/usr/bin/env python3

import os
from setuptools import setup
import scrape

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "scrape",
    version = scrape.__version__,
    author = scrape.__author__,
    description = (scrape.__doc__),
    keywords = "Web Image Scraper",
    url = "https://github.com/jaschon/scrape",
    packages=['scrape', 'bin'],
    long_description=read('README.md'),
    install_requires=read('requirements.txt').splitlines(),
    scripts=['bin/scrape',],
    test_suite="tests", 
)
