#!/usr/bin/env python3
"""
Basic usage examples for ACCR-Replace
Demonstrates common use cases and API patterns
"""

import sys
import os

# Add parent directory to path to import ACCR-Replace
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from ACCR_Replace import Matcher, create_matcher, match_text
    HAS_ACCR_REPLACE = True
except ImportError:
    HAS_ACCR_REPLACE = False
    print("Warning: ACCR-Replace not available. Install or compile first.")


def example_basic_ac_matching():
    """Example: Basic AC automaton matching"""
    print("=== Basic AC Automaton Matching ===")
    
    if not HAS_ACCR_REPLACE:
        print("ACCR-Replace not available")
        return
    
    # Create matcher with string patterns
    patterns = ["apple", "banana", "orange", "grape"]
    matcher = Matcher(patterns=patterns)
    
    # Test text
    text = "I like apple and banana, but sometimes I prefer orange or grape."
    
    # Perform matching
    matches = matcher.match(text.encode('utf-8'))
    
    print(f"Text: {text}")
    print(f"Patterns: {patterns}")
    print(f"Found {len(matches)} matches:")
    
    for match in matches:
        print(f"  - {match['pattern']} at position {match['start']}-{match['end']}")


def example_regex_matching():
    """Example: Regular expression matching"""
    print("\n=== Regular Expression Matching ===")
    
    if not HAS_ACCR_REPLACE:
        print("ACCR-Replace not available")
        return
    
    # Create matcher with regex patterns
    regex_patterns = [
        r"\d{3}-\d{2}-\d{4}",  # SSN format
        r"[A-Z]{3}",           # Three uppercase letters
        r"\b\w{6,}\b",         # Words with 6+ characters
    ]
    matcher = Matcher(regex=regex_patterns)
    
    # Test text
    text = "My SSN is 123-45-6789 and I work at ABC Corp. Some long words: beautiful, wonderful, extraordinary."
    
    # Perform matching
    matches = matcher.match(text.encode('utf-8'))
    
    print(f"Text: {text}")
    print(f"Regex patterns: {regex_patterns}")
    print(f"Found {len(matches)} matches:")
    
    for match in matches:
        matched_text = text[match['start']:match['end']]
        print(f"  - {match['pattern']}: '{matched_text}' at position {match['start']}-{match['end']}")


def example_combined_matching():
    """Example: Combined AC and regex matching"""
    print("\n=== Combined AC and Regex Matching ===")
    
    if not HAS_ACCR_REPLACE:
        print("ACCR-Replace not available")
        return
    
    # Create matcher with both AC patterns and regex
    patterns = ["error", "warning", "critical"]
    regex_patterns = [
        r"\d{4}-\d{2}-\d{2}",  # Date format
        r"\[.*?\]",            # Anything in brackets
    ]
    matcher = Matcher(patterns=patterns, regex=regex_patterns)
    
    # Test log text
    text = """
    [2024-01-15] ERROR: Database connection failed
    [2024-01-15] WARNING: Retrying connection...
    [2024-01-15] INFO: Connection established
    [2024-01-16] CRITICAL: System crash detected
    """
    
    # Perform matching
    matches = matcher.match(text.encode('utf-8'))
    
    print("Log text analyzed:")
    print(f"AC patterns: {patterns}")
    print(f"Regex patterns: {regex_patterns}")
    print(f"Found {len(matches)} total matches:")
    
    # Group matches by type
    ac_matches = [m for m in matches if m['type'] == 'ac']
    regex_matches = [m for m in matches if m['type'] == 'regex']
    
    print(f"  - AC matches: {len(ac_matches)}")
    print(f"  - Regex matches: {len(regex_matches)}")
    
    for match in matches:
        matched_text = text[match['start']:match['end']]
        print(f"    {match['type'].upper()}: {match['pattern']} -> '{matched_text}'")


def example_streaming_mode():
    """Example: Streaming mode for large data"""
    print("\n=== Streaming Mode Example ===")
    
    if not HAS_ACCR_REPLACE:
        print("ACCR-Replace not available")
        return
    
    # Create streaming matcher
    patterns = ["hello", "world", "test"]
    matcher = Matcher(patterns=patterns, streaming=True)
    
    # Simulate streaming data (e.g., from a file or network)
    data_chunks = [
        "This is a hello ",
        "message to the world. ",
        "This is just a test ",
        "of the streaming functionality."
    ]
    
    print("Processing data in chunks:")
    total_matches = 0
    
    for i, chunk in enumerate(data_chunks, 1):
        print(f"  Chunk {i}: '{chunk.strip()}'")
        matches = matcher.feed(chunk.encode('utf-8'))
        
        if matches:
            print(f"    Found {len(matches)} matches in this chunk:")
            for match in matches:
                matched_text = chunk[match['start']:match['end']]
                print(f"      - {match['pattern']}: '{matched_text}'")
            total_matches += len(matches)
        else:
            print("    No matches in this chunk")
    
    print(f"\nTotal matches found: {total_matches}")


def example_convenience_functions():
    """Example: Using convenience functions"""
    print("\n=== Convenience Functions ===")
    
    if not HAS_ACCR_REPLACE:
        print("ACCR-Replace not available")
        return
    
    # Quick one-time matching
    text = "Quick test with number 123 and word example"
    patterns = ["test", "example"]
    regex = [r"\d+"]
    
    print(f"Text: {text}")
    print(f"Patterns: {patterns}")
    print(f"Regex: {regex}")
    
    # Use match_text convenience function
    matches = match_text(text, patterns=patterns, regex=regex)
    
    print(f"Found {len(matches)} matches:")
    for match in matches:
        matched_text = text[match['start']:match['end']]
        print(f"  - {match['type']}: {match['pattern']} -> '{matched_text}'")
    
    # Use create_matcher convenience function
    print("\nUsing create_matcher:")
    matcher = create_matcher(patterns=patterns, regex=regex)
    print(f"Matcher created: {matcher}")


def example_error_handling():
    """Example: Error handling and edge cases"""
    print("\n=== Error Handling Examples ===")
    
    if not HAS_ACCR_REPLACE:
        print("ACCR-Replace not available")
        return
    
    # Empty patterns
    print("Testing with empty patterns:")
    matcher = Matcher(patterns=[], regex=[])
    matches = matcher.match("test text".encode('utf-8'))
    print(f"  Empty patterns: {len(matches)} matches")
    
    # Invalid regex (should handle gracefully)
    print("Testing with invalid regex:")
    try:
        matcher = Matcher(regex=[r"invalid(regex"])  # Unclosed group
        matches = matcher.match("test".encode('utf-8'))
        print(f"  Invalid regex handled: {len(matches)} matches")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Streaming mode without initialization
    print("Testing streaming mode errors:")
    try:
        matcher = Matcher(streaming=True)
        # Forgot to call build()
        matches = matcher.feed(b"test")
        print(f"  Should not reach here")
    except RuntimeError as e:
        print(f"  Expected error: {e}")


if __name__ == "__main__":
    print("ACCR-Replace Usage Examples")
    print("=" * 50)
    
    example_basic_ac_matching()
    example_regex_matching()
    example_combined_matching()
    example_streaming_mode()
    example_convenience_functions()
    example_error_handling()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
