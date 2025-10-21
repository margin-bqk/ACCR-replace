#!/usr/bin/env python
"""
Setup script for fastmatcher package
Builds Cython extensions for high-performance text matching
"""

import os
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Define Cython extensions
extensions = [
    Extension(
        "fastmatcher.matcher",
        ["fastmatcher/matcher.pyx"],
        include_dirs=[numpy.get_include()],
        language="c",
    ),
    Extension(
        "fastmatcher.ac_automaton",
        ["fastmatcher/ac_automaton.pyx"],
        include_dirs=[numpy.get_include()],
        language="c",
    ),
    Extension(
        "fastmatcher.regex_engine",
        ["fastmatcher/regex_engine.pyx"],
        include_dirs=[numpy.get_include()],
        language="c",
    ),
    Extension(
        "fastmatcher.buffer",
        ["fastmatcher/buffer.pyx"],
        include_dirs=[numpy.get_include()],
        language="c",
    ),
]

# Cython compiler directives
compiler_directives = {
    "language_level": 3,
    "boundscheck": False,
    "wraparound": False,
    "initializedcheck": False,
    "nonecheck": False,
    "cdivision": True,
    "infer_types": True,
}

if __name__ == "__main__":
    setup(
        ext_modules=cythonize(
            extensions,
            compiler_directives=compiler_directives,
            annotate=True,  # Generate HTML annotation files for debugging
        ),
        zip_safe=False,
    )
