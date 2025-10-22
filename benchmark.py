#!/usr/bin/env python3
"""
Performance benchmark for ACCR-Replace
Compares performance with pure Python implementations
"""

import time
import timeit
import re
from collections import defaultdict

# Try to import our library (may not work until compiled)
try:
    from ACCR_Replace import Matcher
    HAS_ACCR_REPLACE = True
except ImportError:
    HAS_ACCR_REPLACE = False
    print("Warning: ACCR-Replace not available. Install or compile first.")


class PurePythonAC:
    """Pure Python implementation of AC automaton for comparison"""
    
    def __init__(self, patterns):
        self.patterns = patterns
        self.root = {}
        self.fail = {}
        self.output = defaultdict(list)
        self.node_id = 0
        self._build()
    
    def _build(self):
        """Build the AC automaton"""
        # Build goto function (trie)
        for pattern in self.patterns:
            node = self.root
            for char in pattern:
                node = node.setdefault(char, {})
            node.setdefault('*output*', []).append(pattern)
        
        # Build failure links using BFS
        queue = []
        for char, node in self.root.items():
            if char != '*output*':
                self.fail[id(node)] = self.root
                queue.append(node)
        
        while queue:
            current = queue.pop(0)
            for char, node in current.items():
                if char == '*output*':
                    continue
                
                fail_node = self.fail.get(id(current), self.root)
                while fail_node is not None and char not in fail_node:
                    fail_node = self.fail.get(id(fail_node), None)
                
                if fail_node is None:
                    self.fail[id(node)] = self.root
                else:
                    self.fail[id(node)] = fail_node[char]
                
                # Collect outputs
                if '*output*' in self.fail.get(id(node), {}):
                    self.output[id(node)].extend(self.fail[id(node)]['*output*'])
                if '*output*' in node:
                    self.output[id(node)].extend(node['*output*'])
                
                queue.append(node)
    
    def search(self, text):
        """Search for patterns in text"""
        matches = []
        current = self.root
        
        for i, char in enumerate(text):
            while current is not None and char not in current:
                current = self.fail.get(id(current), None)
            
            if current is None:
                current = self.root
                continue
            
            current = current[char]
            
            # Check for matches
            if id(current) in self.output:
                for pattern in self.output[id(current)]:
                    start = i - len(pattern) + 1
                    matches.append({
                        'pattern': pattern,
                        'start': start,
                        'end': i + 1
                    })
        
        return matches


def benchmark_ac_automaton():
    """Benchmark AC automaton performance"""
    print("=== AC Automaton Performance Benchmark ===")
    
    # Test data
    patterns = ["apple", "banana", "orange", "grape", "kiwi", "mango", "pear", "peach"]
    text = "I like apple and banana with orange juice, but sometimes I prefer grape or kiwi. Mango is also good, and pear with peach is delicious." * 1000
    
    # Pure Python implementation
    print("Testing Pure Python AC Automaton...")
    python_ac = PurePythonAC(patterns)
    
    start_time = time.time()
    python_matches = python_ac.search(text)
    python_time = time.time() - start_time
    
    print(f"Pure Python: {len(python_matches)} matches in {python_time:.4f} seconds")
    
    # ACCR-Replace implementation (if available)
    if HAS_ACCR_REPLACE:
        print("Testing ACCR-Replace AC Automaton...")
        accr_matcher = Matcher(patterns=patterns)
        
        start_time = time.time()
        accr_matches = accr_matcher.match(text.encode('utf-8'))
        accr_time = time.time() - start_time
        
        print(f"ACCR-Replace: matches in {accr_time:.4f} seconds")
        print(f"Speedup: {python_time/accr_time:.2f}x")
    else:
        print("ACCR-Replace not available for comparison")


def benchmark_regex_matching():
    """Benchmark regex matching performance"""
    print("\n=== Regex Matching Performance Benchmark ===")
    
    # Test data
    regex_patterns = [
        r"\d{3}-\d{2}-\d{4}",  # SSN
        r"[A-Z]{3}",           # Three uppercase letters
        r"\b\w{5,10}\b",       # Words of length 5-10
        r"\d+\.\d+",           # Decimal numbers
    ]
    text = "My SSN is 123-45-6789 and code is ABC. Some words: apple banana orange. Numbers: 3.14, 2.71, 1.41." * 500
    
    # Pure Python regex
    print("Testing Pure Python Regex...")
    compiled_patterns = [re.compile(pattern) for pattern in regex_patterns]
    
    start_time = time.time()
    python_matches = []
    for pattern in compiled_patterns:
        for match in pattern.finditer(text):
            python_matches.append({
                'pattern': pattern.pattern,
                'start': match.start(),
                'end': match.end(),
                'matched': match.group()
            })
    python_time = time.time() - start_time
    
    print(f"Pure Python: {len(python_matches)} matches in {python_time:.4f} seconds")
    
    # ACCR-Replace regex (if available)
    if HAS_ACCR_REPLACE:
        print("Testing ACCR-Replace Regex...")
        accr_matcher = Matcher(regex=regex_patterns)
        
        start_time = time.time()
        accr_matches = accr_matcher.match(text.encode('utf-8'))
        accr_time = time.time() - start_time
        
        print(f"ACCR-Replace: matches in {accr_time:.4f} seconds")
        print(f"Speedup: {python_time/accr_time:.2f}x")
    else:
        print("ACCR-Replace not available for comparison")


def benchmark_streaming():
    """Benchmark streaming performance"""
    print("\n=== Streaming Performance Benchmark ===")
    
    if not HAS_ACCR_REPLACE:
        print("ACCR-Replace not available for streaming benchmark")
        return
    
    patterns = ["error", "warning", "info", "debug", "critical"]
    
    # Generate test data
    chunks = []
    for i in range(1000):
        chunk = f"Log entry {i}: This is a test message with some keywords like error, warning, and info. "
        if i % 100 == 0:
            chunk += "CRITICAL error detected! "
        chunks.append(chunk.encode('utf-8'))
    
    # Batch mode
    print("Testing Batch Mode...")
    batch_matcher = Matcher(patterns=patterns, streaming=False)
    combined_text = b"".join(chunks)
    
    start_time = time.time()
    batch_matches = batch_matcher.match(combined_text)
    batch_time = time.time() - start_time
    
    print(f"Batch Mode: {len(batch_matches)} matches in {batch_time:.4f} seconds")
    
    # Streaming mode
    print("Testing Streaming Mode...")
    stream_matcher = Matcher(patterns=patterns, streaming=True)
    
    start_time = time.time()
    stream_matches = []
    for chunk in chunks:
        matches = stream_matcher.feed(chunk)
        stream_matches.extend(matches)
    stream_time = time.time() - start_time
    
    print(f"Streaming Mode: {len(stream_matches)} matches in {stream_time:.4f} seconds")
    print(f"Streaming overhead: {stream_time/batch_time:.2f}x")


def memory_usage_demo():
    """Demo memory usage patterns"""
    print("\n=== Memory Usage Demo ===")
    
    if not HAS_ACCR_REPLACE:
        print("ACCR-Replace not available for memory demo")
        return
    
    # Test with many patterns
    many_patterns = [f"pattern_{i}" for i in range(1000)]
    matcher = Matcher(patterns=many_patterns)
    
    print(f"Built AC automaton with {len(many_patterns)} patterns")
    print("Memory usage demo completed (internal attributes not accessible)")
    
    # Test buffer memory
    stream_matcher = Matcher(patterns=["test"], streaming=True)
    print("Stream buffer initialized successfully")


if __name__ == "__main__":
    print("ACCR-Replace Performance Benchmark Suite")
    print("=" * 50)
    
    benchmark_ac_automaton()
    benchmark_regex_matching()
    benchmark_streaming()
    memory_usage_demo()
    
    print("\n" + "=" * 50)
    print("Benchmark completed!")
