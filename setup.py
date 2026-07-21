#!/usr/bin/env python
"""
Setup script for ACCR-Replace package
Supports both Cython compilation and pure Python implementation
"""

import os
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

# Read the README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Cython extensions - 只编译主 matcher 模块
extensions = [
    Extension(
        "ACCR_Replace.matcher_cython",
        ["ACCR_Replace/matcher.pyx"],
        language="c",
    ),
]

setup(
    name="ACCR-Replace",
    version="0.1.0",
    author="ACCR-Replace Team",
    author_email="your-email@example.com",
    description="High-performance text matching library with AC automaton and regex support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/ACCR-Replace",
    packages=find_packages(),
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
        },
    ),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "Cython>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add any command-line tools here if needed
        ],
    },
)
