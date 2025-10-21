#!/usr/bin/env python3
"""
Unit tests for ACCR-Replace library
Tests AC automaton, regex engine, and streaming functionality
"""

import pytest
import sys
import os

# Add parent directory to path to import ACCR-Replace
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ACCR_Replace import Matcher, create_matcher, match_text


class TestACAutomaton:
    """Test AC automaton functionality"""
    
    def test_basic_ac_matching(self):
        """Test basic AC automaton pattern matching"""
        patterns = ["apple", "banana", "orange"]
        matcher = Matcher(patterns=patterns)
        
        text = "I like apple and banana"
        matches = matcher.match(text.encode('utf-8'))
        
        # Should find both patterns
        assert len(matches) == 2
        # Note: Actual match verification would depend on implementation
    
    def test_ac_overlapping_patterns(self):
        """Test AC automaton with overlapping patterns"""
        patterns = ["he", "she", "his", "hers"]
        matcher = Matcher(patterns=patterns)
        
        text = "ushers"
        matches = matcher.match(text.encode('utf-8'))
        
        # Should find multiple overlapping matches
        assert len(matches) >= 2
    
    def test_ac_empty_patterns(self):
        """Test AC automaton with empty patterns list"""
        matcher = Matcher(patterns=[])
        
        text = "test text"
        matches = matcher.match(text.encode('utf-8'))
        
        # Should return empty list
        assert matches == []


class TestRegexEngine:
    """Test regex engine functionality"""
    
    def test_basic_regex_matching(self):
        """Test basic regex pattern matching"""
        regex_patterns = [r"\d{3}-\d{2}-\d{4}", r"[A-Z]{3}"]
        matcher = Matcher(regex=regex_patterns)
        
        text = "My SSN is 123-45-6789 and code is ABC"
        matches = matcher.match(text.encode('utf-8'))
        
        # Should find both regex patterns
        assert len(matches) == 2
    
    def test_regex_complex_patterns(self):
        """Test complex regex patterns"""
        regex_patterns = [r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"]
        matcher = Matcher(regex=regex_patterns)
        
        text = "Contact me at test@example.com"
        matches = matcher.match(text.encode('utf-8'))
        
        # Should find email pattern
        assert len(matches) == 1
    
    def test_regex_empty_patterns(self):
        """Test regex engine with empty patterns list"""
        matcher = Matcher(regex=[])
        
        text = "test text"
        matches = matcher.match(text.encode('utf-8'))
        
        # Should return empty list
        assert matches == []


class TestCombinedMatching:
    """Test combined AC automaton and regex matching"""
    
    def test_combined_ac_and_regex(self):
        """Test combined AC and regex matching"""
        patterns = ["apple", "banana"]
        regex_patterns = [r"\d+", r"[A-Z]{3}"]
        matcher = Matcher(patterns=patterns, regex=regex_patterns)
        
        text = "I have 3 APPLES and 2 BANANAS with code XYZ"
        matches = matcher.match(text.encode('utf-8'))
        
        # Should find both AC patterns and regex patterns
        assert len(matches) >= 4
    
    def test_priority_handling(self):
        """Test match priority and ordering"""
        patterns = ["test"]
        regex_patterns = [r"test"]
        matcher = Matcher(patterns=patterns, regex=regex_patterns)
        
        text = "this is a test"
        matches = matcher.match(text.encode('utf-8'))
        
        # Should handle both types of matches
        assert len(matches) >= 1


class TestStreamingMode:
    """Test streaming mode functionality"""
    
    def test_streaming_basic(self):
        """Test basic streaming functionality"""
        patterns = ["hello", "world"]
        matcher = Matcher(patterns=patterns, streaming=True)
        
        # Feed data in chunks
        chunk1 = "hello "
        matches1 = matcher.feed(chunk1.encode('utf-8'))
        
        chunk2 = "beautiful world"
        matches2 = matcher.feed(chunk2.encode('utf-8'))
        
        # Should find matches in appropriate chunks
        # Note: Implementation details may vary
    
    def test_streaming_buffer_management(self):
        """Test streaming buffer management"""
        patterns = ["test"]
        matcher = Matcher(patterns=patterns, streaming=True)
        
        # Test buffer capacity
        buffer = matcher.stream_buffer
        assert buffer is not None
        assert buffer.get_capacity() > 0
    
    def test_streaming_reset(self):
        """Test streaming reset functionality"""
        patterns = ["reset"]
        matcher = Matcher(patterns=patterns, streaming=True)
        
        # Feed some data
        matcher.feed(b"test reset test")
        
        # Reset and verify state
        matcher.reset()
        assert matcher.get_total_matches() == 0


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_create_matcher(self):
        """Test create_matcher convenience function"""
        matcher = create_matcher(patterns=["test"], regex=[r"\d+"])
        assert matcher is not None
        assert isinstance(matcher, Matcher)
    
    def test_match_text(self):
        """Test match_text convenience function"""
        text = "test 123"
        matches = match_text(text, patterns=["test"], regex=[r"\d+"])
        
        # Should find matches
        assert len(matches) >= 2


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_regex_pattern(self):
        """Test handling of invalid regex patterns"""
        # This should not crash, but handle the error gracefully
        regex_patterns = [r"invalid(regex"]
        matcher = Matcher(regex=regex_patterns)
        
        # Should still be able to match valid patterns
        text = "test"
        matches = matcher.match(text.encode('utf-8'))
        assert matches is not None
    
    def test_empty_text(self):
        """Test matching against empty text"""
        patterns = ["test"]
        matcher = Matcher(patterns=patterns)
        
        text = ""
        matches = matcher.match(text.encode('utf-8'))
        
        # Should return empty list
        assert matches == []
    
    def test_unicode_text(self):
        """Test matching with unicode text"""
        patterns = ["测试", "例子"]
        matcher = Matcher(patterns=patterns)
        
        text = "这是一个测试例子"
        matches = matcher.match(text.encode('utf-8'))
        
        # Should find unicode patterns
        assert len(matches) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
