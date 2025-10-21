# ACCR-Replace

A high-performance text matching library that combines AC automaton, regular expressions, and streaming input support, accelerated with Cython.

## Features

- **AC Automaton**: Efficient multi-pattern string matching using Aho-Corasick algorithm
- **Regular Expressions**: PCRE2-based regex matching with Python `re` compatibility
- **Streaming Support**: Process data incrementally with configurable buffer sizes
- **High Performance**: Cython-accelerated implementation for 10x+ speedup over pure Python
- **Unicode Support**: Full Unicode text matching capabilities
- **Easy API**: Simple Python interface with familiar patterns

## Installation

```bash
# Install from source
git clone https://github.com/your-org/ACCR-Replace.git
cd ACCR-Replace
pip install -e .

# Or install dependencies for development
pip install -e ".[dev]"
```

## Quick Start

```python
from ACCR_Replace import Matcher

# Create a matcher with AC patterns and regex
matcher = Matcher(
    patterns=["apple", "banana", "orange"],
    regex=[r"\d{4}-\d{2}-\d{2}", r"[A-Z]{3}"],
    streaming=False  # Set to True for streaming mode
)

# Match against text
text = "I have 3 apples and 2 bananas from 2024-01-15 with code XYZ"
matches = matcher.match(text.encode('utf-8'))

for match in matches:
    print(f"Found {match['type']} match: {match['pattern']} at position {match['start']}-{match['end']}")
```

## Streaming Mode

```python
from ACCR_Replace import Matcher

# Create streaming matcher
matcher = Matcher(
    patterns=["error", "warning", "critical"],
    streaming=True
)

# Process data in chunks
for chunk in read_log_stream():
    matches = matcher.feed(chunk.encode('utf-8'))
    for match in matches:
        print(f"Found {match['pattern']} in stream")
```

## API Reference

### Matcher Class

```python
from ACCR_Replace import Matcher
```

**Parameters:**
- `patterns`: List of string patterns for AC automaton matching
- `regex`: List of regex patterns for regular expression matching
- `streaming`: Enable streaming mode for incremental processing

**Methods:**
- `build(patterns=[], regex=[])`: Build/re-build matching engines
- `match(text)`: Match against complete text (batch mode)
- `feed(chunk)`: Feed data chunk (streaming mode only)
- `reset()`: Reset matcher state (clears buffer and counters)
- `get_total_matches()`: Get total matches found
- `is_streaming()`: Check if streaming mode is enabled

### Convenience Functions

```python
from ACCR_Replace import create_matcher, match_text

# Create matcher instance
matcher = create_matcher(patterns=["test"], regex=[r"\d+"])

# Quick one-time matching
matches = match_text("test 123", patterns=["test"], regex=[r"\d+"])
```

## Performance

ACCR-Replace is designed for high-performance text processing:

- **AC Automaton**: O(n + m + z) time complexity where n is text length, m is total pattern length, z is number of matches
- **Regex Engine**: PCRE2-optimized matching with JIT compilation
- **Streaming**: Configurable buffer sizes with minimal overhead
- **Memory**: Efficient data structures with Cython memory management

## Examples

### Basic Usage

```python
from ACCR_Replace import Matcher

# Simple pattern matching
matcher = Matcher(patterns=["hello", "world"])
matches = matcher.match("hello beautiful world".encode('utf-8'))

# Combined AC and regex
matcher = Matcher(
    patterns=["email", "phone"],
    regex=[r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", r"\d{3}-\d{3}-\d{4}"]
)
```

### File Processing

```python
def process_large_file(filename, patterns, regex_patterns):
    matcher = Matcher(patterns=patterns, regex=regex_patterns, streaming=True)
    
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(4096)  # 4KB chunks
            if not chunk:
                break
            matches = matcher.feed(chunk)
            yield from matches
```

### Log Analysis

```python
import re
from ACCR_Replace import Matcher

# Common log patterns
error_patterns = ["ERROR", "CRITICAL", "FAILED"]
regex_patterns = [
    r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
    r"\[.*?\]",
    r"thread-\d+"
]

matcher = Matcher(patterns=error_patterns, regex=regex_patterns, streaming=True)

for line in sys.stdin:
    matches = matcher.feed(line.encode('utf-8'))
    if matches:
        print(f"Found issues: {matches}")
```

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/your-org/ACCR-Replace.git
cd ACCR-Replace

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Build Cython extensions
python setup.py build_ext --inplace
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ACCR_Replace

# Run specific test categories
pytest tests/test_matcher.py::TestACAutomaton
pytest tests/test_matcher.py::TestRegexEngine
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Aho-Corasick algorithm for efficient multi-pattern matching
- PCRE2 library for high-performance regular expressions
- Cython project for Python C extensions
- Python community for excellent tooling and libraries
