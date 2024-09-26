from dataclasses import dataclass


# Global variables
# Number of available plates (bins) that should not be exceeded
N_PLATES: int = 100
# Fixed width of plates
WIDTH_PLATES: int = 6000
# Fixed height of plates
HEIGHT_PLATES: int = 3210
# Minimum distance between two consecutive 1-cuts (except wastes)
MIN_1_CUT: int = 100
# Maximum distance between two consecutive 1-cuts (except residual)
MAX_1_CUT: int = 3500
# Minimum distance between two consecutive 2-cuts (except wastes)
MIN_2_CUT: int = 100
# Minimum width and height of wastes
MIN_WASTE: int = 20


@dataclass
class Defect:
    """Class for a defect on a bin."""
    id: int
    x: int
    y: int
    width: int
    height: int


@dataclass
class Bin:
    """Class for a bin, so a jumbo glass plate."""
    id: int
    defects: list[Defect]


@dataclass
class Item:
    """Class for a item to cut."""
    id: int
    width: int
    length: int    


@dataclass
class Stack:
    """"Class for a stack of items to cut in a specific order."""
    id: int
    sequence: tuple[Item]

    
@dataclass
class Batch:
    """Class for a stack of items to cut."""
    stacks: list[Stack]
    