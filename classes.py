from dataclasses import dataclass
from typing import Optional, List
from collections import defaultdict
from itertools import count


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
    """
    Class for a defect on a bin.
    
    Attributes:
        id (int): Identifier of a defect.
        x (int): X coordinate of the bottom left corner of the defect in its plate.
        y (int): Y coordinate of the bottom left corner of the defect in its plate.
        width (int): Width along the x-axis of the defect.
        height (int): Height along the y-axis of the defect.
    """
    id: int
    x: int
    y: int
    width: int
    height: int


@dataclass
class Bin:
    """
    Class for a bin, so a jumbo glass plate.
    
    Attributes:
        id (int): Identifier of the bin.
        width (int): Width of the bin.
        height (int): Height of the bin.
        defects (list[Defect]): List of defects present in the bin.
    """
    id: int
    width: int
    height: int
    defects: list[Defect]


@dataclass
class Item:
    """
    Class for a item to cut.
    
    Attributes:
        id (int): Identifier of the item.
        width (int): Width of the item.
        length (int): Length of the item with length >= width.
    """
    id: int
    width: int
    length: int    


@dataclass
class Stack:
    """"
    Class for a stack of items to cut in a specific order.
    
    Attributes:
        id (int): Identifier of the stack.
        sequence (tuple[Item]): Sequence of items in the stack.
    """
    id: int
    sequence: tuple[Item]

    
@dataclass
class Batch:
    """
    Class for a stack of items to cut.
    
    Attributes:
        stacks (list[Stack]): List of stacks included in the batch.
    """
    stacks: list[Stack]

@dataclass
class Node:
    """
    Class used to produce the output.
    A node is always a rectangle that may be a plate, a branch (node with children), an item, a waste or a residual.

    Attributes:
        plate_id (int): ID of the plate in the current cutting pattern.
        id (int): Unique identifier for this node.
        x (int): X-coordinate of the node's bottom-left corner.
        y (int): Y-coordinate of the node's bottom-left corner.
        width (int): Node's width.
        height (int): Node's height.
        type (int): Type of node:
            - >= 0: Item ID.
            - -1: Waste.
            - -2: Branch (has children).
            - -3: Residual.
        cut (int): Cut type:
            - 0: Plate.
            - 1-4: Specific cut type.
        parent (Optional[Node]): Parent node, if any.
        children (List[Node]): List of child nodes if it's a branch.
    """
    plate_id: int
    id: int
    x: int
    y: int
    width: int
    height: int
    type: int
    cut: int
    parent: Optional['Node'] = None
    children: List['Node'] = []