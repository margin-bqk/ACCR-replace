"""
High-performance text matching library
Supports AC automaton + regular expressions + streaming input
Accelerated with Cython for high-performance matching
"""

__version__ = "0.1.0"
__author__ = "ACCR-replace Team"

from .matcher import Matcher

__all__ = ["Matcher"]
