"""
Simplified regex engine implementation in Cython
Basic regex matching functionality
"""

from libc.stdint cimport uint32_t
from cpython.bytes cimport PyBytes_AsString
import cython
import re


cdef class RegexEngine:
    """Simplified regex engine for pattern matching"""
    
    def __cinit__(self):
        """Initialize the regex engine"""
        self.patterns = []
        self.compiled_patterns = []
        self.built = False
    
    cpdef void build(self, list patterns):
        """Build the regex engine from patterns"""
        self.patterns = patterns
        self.compiled_patterns = []
        
        for pattern in patterns:
            try:
                compiled = re.compile(pattern)
                self.compiled_patterns.append(compiled)
            except re.error:
                # Skip invalid patterns
                pass
        
        self.built = True
    
    cpdef list match(self, bytes text, uint32_t text_len=0):
        """Match regex patterns against text"""
        if not self.built:
            return []
        
        cdef list matches = []
        cdef str text_str = text.decode('utf-8')
        
        for compiled in self.compiled_patterns:
            for match_obj in compiled.finditer(text_str):
                matches.append({
                    'pattern': compiled.pattern,
                    'start': match_obj.start(),
                    'end': match_obj.end(),
                    'matched': match_obj.group()
                })
        
        return matches
