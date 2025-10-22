#!/usr/bin/env python
"""
Simple Cython compilation setup
Focuses on basic compilation without complex dependencies
"""

from setuptools import setup, Extension
from Cython.Build import cythonize

# Simple Cython extension for basic functionality
extensions = [
    Extension(
        "ACCR_Replace.matcher_cython",
        ["ACCR_Replace/matcher.pyx"],
        language="c++",
    ),
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
        },
    )
)
