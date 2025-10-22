"""
Python wrapper for Cython matcher module
Provides fallback implementation if Cython modules are not compiled
"""

import sys
import warnings

# Check if Cython modules are available
try:
    from .ac_automaton import ACAutomaton
    from .regex_engine import RegexEngine
    from .buffer import StreamBuffer
    HAS_CYTHON = True
except ImportError:
    HAS_CYTHON = False
    warnings.warn(
        "Cython modules not available. Using pure Python implementation. "
        "Performance will be significantly slower. Run 'python setup.py build_ext --inplace' to compile Cython extensions.",
        RuntimeWarning
    )

# Pure Python implementation (fallback)
class Matcher:
    """Pure Python implementation of Matcher (fallback)"""
    
    def __init__(self, patterns=None, regex=None, streaming=False):
        self.patterns = patterns or []
        self.regex = regex or []
        self.streaming = streaming
        self._total_matches = 0
        
        # Build matching engines
        self.build(patterns, regex)
    
    def build(self, patterns=None, regex=None):
        """Build/re-build matching engines"""
        if patterns is not None:
            self.patterns = patterns
        if regex is not None:
            self.regex = regex
        
        # Simple implementation - just store patterns
        self._ac_patterns = self.patterns
        self._regex_patterns = self.regex
    
    def match(self, text):
        """Match against complete text (batch mode)"""
        import re
        
        matches = []
        
        # AC pattern matching (simple substring search)
        for pattern in self._ac_patterns:
            pattern_bytes = pattern.encode('utf-8')
            start = 0
            while True:
                pos = text.find(pattern_bytes, start)
                if pos == -1:
                    break
                matches.append({
                    'pattern': pattern,
                    'start': pos,
                    'end': pos + len(pattern_bytes),
                    'type': 'ac'
                })
                start = pos + 1
        
        # Regex matching
        for pattern in self._regex_patterns:
            try:
                regex = re.compile(pattern)
                for match in regex.finditer(text.decode('utf-8')):
                    matches.append({
                        'pattern': pattern,
                        'start': match.start(),
                        'end': match.end(),
                        'type': 'regex',
                        'matched': match.group()
                    })
            except re.error:
                # Skip invalid regex patterns
                continue
        
        self._total_matches += len(matches)
        return matches
    
    def feed(self, chunk):
        """Feed data chunk (streaming mode only)"""
        if not self.streaming:
            raise RuntimeError("feed() can only be used in streaming mode")
        
        # Simple streaming implementation - just use match
        return self.match(chunk)
    
    def reset(self):
        """Reset matcher state"""
        self._total_matches = 0
    
    def get_total_matches(self):
        """Get total matches found"""
        return self._total_matches
    
    def is_streaming(self):
        """Check if streaming mode is enabled"""
        return self.streaming


def create_matcher(patterns=None, regex=None):
    """Create matcher instance convenience function"""
    return Matcher(patterns=patterns, regex=regex)


def match_text(text, patterns=None, regex=None):
    """Quick one-time matching convenience function"""
    matcher = Matcher(patterns=patterns, regex=regex)
    return matcher.match(text.encode('utf-8') if isinstance(text, str) else text)


# Export the same API
__all__ = ["Matcher", "create_matcher", "match_text"]
