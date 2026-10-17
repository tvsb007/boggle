import typing
from typing import Optional, Dict
from collections.abc import Iterator

from py_boggle.boggle_dictionary import BoggleDictionary


class TrieDictionaryIterator:
    """
    Iterator for TrieDictionary that performs depth-first traversal of the Trie,
    yielding words in lexicographic order.
    """

    def __init__(self, root: 'TrieNode'):
        self.root = root
        self.stack: list = []  # Stack of (node, prefix) tuples
        self._initialize_stack()

    def _initialize_stack(self):
        """Initialize the stack with all paths in reverse lexicographic order."""
        if self.root:
            # Push all children of root in reverse order so we pop them in order
            sorted_keys = sorted(self.root.children.keys(), reverse=True)
            for key in sorted_keys:
                self.stack.append((self.root.children[key], key))

    def __iter__(self):
        return self

    def __next__(self) -> str:
        while self.stack:
            node, prefix = self.stack.pop()

            # Push children of current node in reverse order for correct traversal
            sorted_keys = sorted(node.children.keys(), reverse=True)
            for key in sorted_keys:
                self.stack.append((node.children[key], prefix + key))

            # If this node marks the end of a word, return it
            if node.is_word:
                return prefix

        raise StopIteration


class TrieNode:
    """
    Our TrieNode class. Feel free to add new properties/functions, but 
    DO NOT edit the names of the given properties (children and is_word).
    """
    def __init__(self):
        self.children : Dict[str, TrieNode] = {} # maps a child letter to its TrieNode class
        self.is_word = False # whether or not this Node is a valid word ending


class TrieDictionary(BoggleDictionary):
    """
    Your implementation of BoggleDictionary.
    Several functions have been filled in for you from our solution, but you are free to change their implementations.
    Do NOT change the name of self.root, as our autograder will manually traverse using self.root
    """

    def __init__(self):
        self.root : TrieNode = TrieNode()

    def load_dictionary(self, filename: str) -> None:
        # Remember to add every word to the trie, not just the words over some length.
        with open(filename) as wordsfile:
            for line in wordsfile:
                word = line.strip().lower()
                if word:  # Only process non-empty lines
                    node = self.root
                    for char in word:
                        if char not in node.children:
                            node.children[char] = TrieNode()
                        node = node.children[char]
                    node.is_word = True

    def traverse(self, prefix: str) -> Optional[TrieNode]:
        """
        Traverse will traverse the Trie down a given path of letters `prefix`.
        If there is ever a missing child node, then returns None.
        Otherwise, returns the TrieNode referenced by `prefix`.
        """
        prefix = prefix.lower()
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def is_prefix(self, prefix: str) -> bool:
        node = self.traverse(prefix)
        return node is not None

    def contains(self, word: str) -> bool:
        node = self.traverse(word)
        return node is not None and node.is_word

    def __iter__(self) -> typing.Iterator[str]:
        return TrieDictionaryIterator(self.root)

