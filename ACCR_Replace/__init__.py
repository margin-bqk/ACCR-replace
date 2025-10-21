"""
High-performance text matching library
Supports AC automaton + regular expressions + streaming input
Accelerated with Cython for high-performance matching
"""

__version__ = "0.1.0"
__author__ = "ACCR-Replace Team"

from .matcher import Matcher, create_matcher, match_text

__all__ = ["Matcher", "create_matcher", "match_text"]
