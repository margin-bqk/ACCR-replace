# AC Automaton implementation
# High-performance Aho-Corasick automaton for multi-pattern matching

from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memcpy, memset
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AsString
import cython

# Import definitions
cimport ac_automaton

# Constants
DEF ALPHABET_SIZE = 256  # ASCII character set

cdef class ACAutomaton:
    """
    Aho-Corasick automaton for efficient multi-pattern string matching
    """
    
    def __cinit__(self):
        """Initialize the automaton with empty root node"""
        self.root = self._create_node()
        self.node_count = 1
        self.patterns = []
        self.pattern_to_id = {}
    
    def __dealloc__(self):
        """Clean up memory when object is destroyed"""
        if self.root:
            self._free_tree(self.root)
    
    cdef ACNode* _create_node(self) nogil:
        """Create a new AC automaton node"""
        cdef ACNode* node = <ACNode*>PyMem_Malloc(sizeof(ACNode))
        if not node:
            return NULL
        
        # Initialize node fields
        node.children = <ACNode**>PyMem_Malloc(ALPHABET_SIZE * sizeof(ACNode*))
        if not node.children:
            PyMem_Free(node)
            return NULL
        
        memset(node.children, 0, ALPHABET_SIZE * sizeof(ACNode*))
        node.fail = NULL
        node.output = NULL
        node.output_count = 0
        node.is_final = 0
        node.character = 0
        
        return node
    
    cdef void _free_tree(self, ACNode* node) nogil:
        """Recursively free the automaton tree"""
        cdef uint32_t i
        if node:
            for i in range(ALPHABET_SIZE):
                if node.children[i]:
                    self._free_tree(node.children[i])
            if node.output:
                PyMem_Free(node.output)
            if node.children:
                PyMem_Free(node.children)
            PyMem_Free(node)
    
    cpdef void build(self, list patterns):
        """
        Build the AC automaton from a list of patterns
        
        Args:
            patterns: List of string patterns to match
        """
        self.patterns = patterns
        self.pattern_to_id = {pattern: i for i, pattern in enumerate(patterns)}
        
        # Build goto function
        self._build_goto(patterns)
        
        # Build failure links
        self._build_failure_links()
        
        # Collect outputs
        self._collect_outputs()
    
    cdef void _build_goto(self, list patterns) nogil:
        """Build the goto function (trie construction)"""
        cdef ACNode* current
        cdef char* pattern_bytes
        cdef uint32_t pattern_len, i, j
        cdef char c
        
        for i in range(len(patterns)):
            pattern_bytes = <char*>PyBytes_AsString(patterns[i])
            pattern_len = len(patterns[i])
            current = self.root
            
            for j in range(pattern_len):
                c = pattern_bytes[j]
                if not current.children[<uint32_t>c]:
                    current.children[<uint32_t>c] = self._create_node()
                    current.children[<uint32_t>c].character = c
                    self.node_count += 1
                current = current.children[<uint32_t>c]
            
            # Mark as final node for this pattern
            current.is_final = 1
    
    cdef void _build_failure_links(self) nogil:
        """Build failure links using BFS"""
        cdef ACNode* current
        cdef ACNode* fail_node
        cdef ACNode* child
        cdef uint32_t i
        cdef list queue = []
        
        # Initialize root's children failure links to root
        for i in range(ALPHABET_SIZE):
            if self.root.children[i]:
                self.root.children[i].fail = self.root
                queue.append(self.root.children[i])
            else:
                self.root.children[i] = self.root
        
        # BFS to build failure links
        while queue:
            current = queue.pop(0)
            
            for i in range(ALPHABET_SIZE):
                if current.children[i]:
                    child = current.children[i]
                    fail_node = current.fail
                    
                    # Find the longest proper suffix that is also a prefix
                    while fail_node != self.root and not fail_node.children[i]:
                        fail_node = fail_node.fail
                    
                    if fail_node.children[i]:
                        child.fail = fail_node.children[i]
                    else:
                        child.fail = self.root
                    
                    queue.append(child)
    
    cdef void _collect_outputs(self) nogil:
        """Collect output functions for each node"""
        cdef list queue = [self.root]
        cdef ACNode* current
        cdef uint32_t i
        
        while queue:
            current = queue.pop(0)
            
            # If failure node has outputs, inherit them
            if current.fail and current.fail.output_count > 0:
                current.output_count = current.fail.output_count
                current.output = <uint32_t*>PyMem_Malloc(current.output_count * sizeof(uint32_t))
                memcpy(current.output, current.fail.output, current.output_count * sizeof(uint32_t))
            
            # Add current node's pattern if it's final
            if current.is_final:
                # This would need pattern ID tracking - simplified for now
                pass
            
            for i in range(ALPHABET_SIZE):
                if current.children[i]:
                    queue.append(current.children[i])
    
    cpdef list search(self, bytes text):
        """
        Search for patterns in the given text
        
        Args:
            text: Input text to search in
            
        Returns:
            List of match positions and pattern IDs
        """
        cdef char* text_bytes = PyBytes_AsString(text)
        cdef uint32_t text_len = len(text)
        return self._search(text_bytes, text_len)
    
    cdef list _search(self, char* text, uint32_t text_len) nogil:
        """Internal search implementation"""
        cdef ACNode* current = self.root
        cdef uint32_t i
        cdef char c
        cdef list matches = []
        cdef MatchResult match
        
        for i in range(text_len):
            c = text[i]
            
            # Follow failure links until we find a valid transition
            while current != self.root and not current.children[<uint32_t>c]:
                current = current.fail
            
            if current.children[<uint32_t>c]:
                current = current.children[<uint32_t>c]
            
            # Check for matches at current node
            if current.is_final:
                # Simplified match collection - would need pattern tracking
                pass
        
        return matches
    
    cpdef uint32_t get_node_count(self):
        """Get the total number of nodes in the automaton"""
        return self.node_count
