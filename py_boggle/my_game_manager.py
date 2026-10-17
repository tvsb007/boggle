import copy
import random
from typing import List, Optional, Set, Tuple

from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.boggle_game import BoggleGame

"""
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************

If you worked in a group on this project, please type the EIDs of your groupmates below (do not include yourself).
Leave it as TODO otherwise.
Groupmate 1: TODO
Groupmate 2: TODO
"""

SHORT = 3
CUBE_SIDES = 6

class MyGameManager(BoggleGame):
    """Your implementation of `BoggleGame`
    """

    def __init__(self):
        """Constructs an empty Boggle Game.

        A newly-constructed game is unplayable.
        The `new_game` method will be called to initialize a playable game.
        Do not call `new_game` here.

        This method is provided for you, but feel free to change it.
        """

        self.board: List[List[str]] # current game board
        self.size: int # board size
        self.words: List[str] # player's current words
        self.dictionary: BoggleDictionary # the dictionary to use
        self.last_added_word: Optional[List[Tuple[int, int]]] # the position of the last added word, or None

    def new_game(self, size: int, cubefile: str, dictionary: BoggleDictionary) -> None:
        """This method is provided for you, but feel free to change it.
        """
        with open(cubefile, 'r') as infile:
            faces = [line.strip() for line in infile]
        cubes = [f.lower() for f in faces if len(f) == CUBE_SIDES]
        if size < 2 or len(cubes) < size*size:
            raise ValueError('ERROR: Invalid Dimensions (size, cubes)')
        random.shuffle(cubes)
        # Set all of the game parameters
        self.board =[[random.choice(cubes[r*size + c]) 
                    for r in range(size)] for c in range(size)]
        self.size = size
        self.words = []
        self.dictionary = dictionary
        self.last_added_word = None


    def get_board(self) -> List[List[str]]:
        """This method is provided for you, but feel free to change it.
        """
        return self.board

    def find_word_in_board(self, word: str) -> Optional[List[Tuple[int, int]]]:
        """Helper method called by add_word()
        Expected behavior:
        Returns an ordered list of coordinates of a word on the board in the same format as get_last_added_word()
        (see documentation in boggle_game.py).
        If `word` is not present on the board, return None.
        """
        word = word.lower()

        # Try starting from each cell on the board
        for r in range(self.size):
            for c in range(self.size):
                visited = set()
                path = []
                if self._dfs_find_word(word, 0, r, c, visited, path):
                    return path

        return None

    def _dfs_find_word(
        self, 
        word: str, 
        word_idx: int, 
        row: int, 
        col: int, 
        visited: set,
        path: List[Tuple[int, int]]
    ) -> bool:
        """DFS helper to find a word path on the board.

        Args:
            word: The word we're looking for (lowercase)
            word_idx: Current index in the word
            row: Current row on the board
            col: Current column on the board
            visited: Set of (row, col) tuples already used in this path
            path: List of (row, col) coordinates found so far

        Returns:
            True if the word is found starting from this position
        """
        # Base case: we've matched all characters
        if word_idx == len(word):
            return True

        # Boundary check
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False

        # Already visited in this path
        if (row, col) in visited:
            return False

        # Character doesn't match
        if self.board[row][col] != word[word_idx]:
            return False

        # Mark as visited and add to path
        visited.add((row, col))
        path.append((row, col))

        # Try all 8 neighbors
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the current cell
                if self._dfs_find_word(word, word_idx + 1, row + dr, col + dc, visited, path):
                    return True

        # Backtrack
        visited.remove((row, col))
        path.pop()
        return False

    def add_word(self, word: str) -> int:
        """This method is provided for you, but feel free to change it.
        """
        word = word.lower()
        if (len(word) > SHORT and word not in self.words and self.dictionary.contains(word)):
            location = self.find_word_in_board(word)
            if location is not None:
                self.last_added_word = location
                self.words.append(word)
                return len(word) - SHORT
        return 0

    def get_last_added_word(self) -> Optional[List[Tuple[int, int]]]:
        """This method is provided for you, but feel free to change it.
        """
        return self.last_added_word

    def set_game(self, board: List[List[str]]) -> None:
        """This method is provided for you, but feel free to change it.
        """
        self.board = [[c.lower() for c in row] for row in board]

    def get_score(self) -> int:
        """This method is provided for you, but feel free to change it.
        """
        return sum([len(word) - SHORT for word in self.words])

    def dictionary_driven_search(self) -> Set[str]:
        """Find all words using a dictionary-driven search.

        The dictionary-driven search attempts to find every word in the
        dictionary on the board.

        Returns:
            A set containing all words found on the board.
        """
        found_words = set()

        # Iterate through all words in the dictionary
        for word in self.dictionary:
            word_lower = word.lower()
            # Only consider words of length 4 or more (scoring requirement)
            if len(word_lower) > SHORT:
                if self.find_word_in_board(word_lower) is not None:
                    found_words.add(word_lower)

        return found_words

    def board_driven_search(self) -> Set[str]:
        """Find all words using a board-driven search.

        The board-driven search constructs a string using every path on
        the board and checks whether each string is a valid word in the
        dictionary.

        Returns:
            A set containing all words found on the board.
        """
        found_words = set()

        # Try starting a search from each cell on the board
        for r in range(self.size):
            for c in range(self.size):
                visited = set()
                path_str = ""
                path_coords = []
                self._dfs_board_search(r, c, visited, path_str, path_coords, found_words)

        return found_words

    def _dfs_board_search(
        self,
        row: int,
        col: int,
        visited: set,
        current_word: str,
        path_coords: List[Tuple[int, int]],
        found_words: Set[str]
    ) -> None:
        """DFS helper for board-driven search.

        Explores all possible paths from a starting position and collects valid words.
        """
        # Boundary check
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return

        # Already visited in this path
        if (row, col) in visited:
            return

        # Add current cell to path
        current_word += self.board[row][col]
        path_coords.append((row, col))
        visited.add((row, col))

        # Check if current word is valid only if it's long enough
        if len(current_word) > SHORT:
            if self.dictionary.contains(current_word.lower()):
                found_words.add(current_word.lower())

        # Prune: if current_word is not a valid prefix, stop exploring this path
        if not self.dictionary.is_prefix(current_word.lower()):
            # Backtrack
            visited.remove((row, col))
            path_coords.pop()
            return

        # Explore all 8 neighbors
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the current cell
                self._dfs_board_search(row + dr, col + dc, visited, current_word, path_coords, found_words)

        # Backtrack
        visited.remove((row, col))
        path_coords.pop()
