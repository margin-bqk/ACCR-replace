"""
Cython implementation of high-performance text matcher
Combines AC automaton and regex engine for optimal performance
"""

from libc.stdint cimport uint32_t, uint64_t
from cpython.bytes cimport PyBytes_AsString
import cython

# Import our modules
from ac_automaton cimport ACAutomaton
from regex_engine cimport RegexEngine
from buffer cimport StreamBuffer


cdef class Matcher:
    """High-performance text matcher combining AC automaton and regex engine"""
    
    def __cinit__(self, patterns=None, regex=None, streaming=False):
        """Initialize matcher with patterns and configuration"""
        self.ac_patterns = patterns or []
        self.regex_patterns = regex or []
        self.streaming_mode = streaming
        self.total_matches = 0
        
        # Initialize engines
        self.ac_automaton = None
        self.regex_engine = None
        self.stream_buffer = None
        
        # Build engines
        self.build(self.ac_patterns, self.regex_patterns)
    
    cpdef void build(self, list patterns=None, list regex=None):
        """Build/re-build matching engines"""
        if patterns is not None:
            self.ac_patterns = patterns
        if regex is not None:
            self.regex_patterns = regex
        
        # Initialize AC automaton if we have patterns
        if self.ac_patterns:
            self.ac_automaton = ACAutomaton()
            self.ac_automaton.build(self.ac_patterns)
        
        # Initialize regex engine if we have regex patterns
        if self.regex_patterns:
            self.regex_engine = RegexEngine()
            self.regex_engine.build(self.regex_patterns)
        
        # Initialize stream buffer if in streaming mode
        if self.streaming_mode and not self.stream_buffer:
            self.stream_buffer = StreamBuffer()
    
    cpdef list match(self, bytes text):
        """Match against complete text (batch mode)"""
        cdef char* text_bytes = PyBytes_AsString(text)
        cdef uint32_t text_len = len(text)
        
        # Process the text
        matches = self._process_chunk(text_bytes, text_len)
        self.total_matches += len(matches)
        return matches
    
    cpdef list feed(self, bytes chunk):
        """Feed data chunk (streaming mode only)"""
        if not self.streaming_mode:
            raise RuntimeError("feed() can only be used in streaming mode")
        
        cdef char* chunk_bytes = PyBytes_AsString(chunk)
        cdef uint32_t chunk_len = len(chunk)
        
        # Process the chunk
        matches = self._process_chunk(chunk_bytes, chunk_len)
        self.total_matches += len(matches)
        return matches
    
    cdef list _process_chunk(self, char* chunk, uint32_t chunk_len):
        """Internal chunk processing"""
        cdef list ac_matches = []
        cdef list regex_matches = []
        
        # AC automaton matching
        if self.ac_automaton:
            ac_matches = self.ac_automaton.search(chunk, chunk_len)
        
        # Regex matching
        if self.regex_engine:
            regex_matches = self.regex_engine.match(chunk, chunk_len)
        
        # Combine and return matches
        return self._combine_matches(ac_matches, regex_matches)
    
    cdef list _combine_matches(self, list ac_matches, list regex_matches):
        """Combine AC and regex matches"""
        cdef list combined_matches = []
        
        # Add AC matches
        for match in ac_matches:
            combined_matches.append({
                'type': 'ac',
                'pattern': match['pattern'],
                'start': match['start'],
                'end': match['end']
            })
        
        # Add regex matches
        for match in regex_matches:
            combined_matches.append({
                'type': 'regex',
                'pattern': match['pattern'],
                'start': match['start'],
                'end': match['end'],
                'matched': match['matched']
            })
        
        return combined_matches
    
    cpdef void reset(self):
        """Reset matcher state"""
        self.total_matches = 0
        if self.stream_buffer:
            self.stream_buffer.reset()
    
    cpdef uint32_t get_total_matches(self):
        """Get total matches found"""
        return self.total_matches
    
    cpdef bint is_streaming(self):
        """Check if streaming mode is enabled"""
        return self.streaming_mode
