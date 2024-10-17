from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum, auto


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


class Place(Enum):
    """
    Enumeration for different directional positions during the trimming process.
    
    Attributes:
        NONE: cannot be cut
        LEFT: means do a vertical cut, and the left is suitable for the item
        RIGHT: do vertical and right is suitable
        DOWN: do horizontal and up is suitable
        UP: do horizontal and down is suitable
    """
    NONE = 0
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()
    UP = auto()

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

    def can_cut_x(self, x: int) -> bool:
        """
            Returns if one can cut through coordinate x.
        """
        for defect in self.defects:
            if defect.x <= x <= defect.x + defect.width: return False
        return True
    
    def can_cut_y(self, y: int) -> bool:
        """
            Returns if one can cut through coordinate y.
        """
        for defect in self.defects:
            if defect.y <= y <= defect.y + defect.width: return False
        return True
    
    def has_defect_in(self, x_low: int, x_high: int , y_low: int, y_high:int) -> bool:
        """
            Returns if there is a defect in a rectangle defined by parameters.
        """
        for defect in self.defects:
            if (
                # Has defect between x values
                (x_low < defect.x < x_high
                or x_low < defect.x + defect.width < x_high
                or (x_low >= defect.x and x_high <= defect.x + defect.width))
                and # and has defect in x values
                (y_low < defect.y < x_high
                or y_low < defect.y + defect.height < y_high
                or (y_low >= defect.y and y_high <= defect.y + defect.height)) 
            ): return True
        return False
    

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
        sequence (list[Item]): Sequence of items in the stack.
    """
    id: int
    sequence: list[Item]

    
@dataclass
class Batch:
    """
    Class for a stack of items to cut.
    
    Attributes:
        stacks (list[Stack]): List of stacks included in the batch.
    """
    stacks: list[Stack]

@dataclass
class Residual:
    """
    Class for a residual glass plate.
    
    Attributes:
        width (int): Width of the bin.
        height (int): Height of the bin.
        defects (list[Defect]): List of defects present in the bin.
    """
    x: int
    y: int
    width: int
    height: int
    defects: list[Defect]

    def can_cut_x(self, x: int) -> bool:
        """
            Returns if one can cut through coordinate x.
        """
        for defect in self.defects:
            if defect.x <= x <= defect.x + defect.width: return False
        return True
    
    def can_cut_y(self, y: int) -> bool:
        """
            Returns if one can cut through coordinate y.
        """
        for defect in self.defects:
            if defect.y <= y <= defect.y + defect.width: return False
        return True
    
    def has_defect_in(self, x_low: int, x_high: int , y_low: int, y_high:int) -> bool:
        """
            Returns if there is a defect in a rectangle defined by parameters.
        """
        for defect in self.defects:
            if (
                # Has defect between x values
                (x_low < defect.x < x_high
                or x_low < defect.x + defect.width < x_high
                or (x_low >= defect.x and x_high <= defect.x + defect.width))
                and # and has defect in x values
                (y_low < defect.y < x_high
                or y_low < defect.y + defect.height < y_high
                or (y_low >= defect.y and y_high <= defect.y + defect.height)) 
            ): return True
        return False
    
    def defects_in(self, x_low: int, x_high: int , y_low: int, y_high:int) -> list[Defect]:
        """
        Checks for defects within the specified rectangular area defined by 
        the given x and y coordinate ranges.

        Parameters:
            x_low (int): The lower x-coordinate of the search area.
            x_high (int): The upper x-coordinate of the search area.
            y_low (int): The lower y-coordinate of the search area.
            y_high (int): The upper y-coordinate of the search area.

        Returns:
            list[Defect]: A list of Defect objects that are within the specified area.
        """
        defects = []
        for defect in self.defects:
            if (
                # Has defect between x values
                (x_low < defect.x < x_high
                or x_low < defect.x + defect.width < x_high
                or (x_low >= defect.x and x_high <= defect.x + defect.width))
                and # and has defect in x values
                (y_low < defect.y < y_high
                or y_low < defect.y + defect.height < y_high
                or (y_low >= defect.y and y_high <= defect.y + defect.height)) 
            ): defects.append(defect)
        return defects
    
    def find_place(self, width: int, length: int, is_vertical: bool) -> tuple[int, int]:
        """
        Finds an available position for a rectangle with the specified width and length, 
        avoiding defects. Starts with bottom left, first go up, then right.

        Parameters:
            width (int): The width of the rectangle to place.
            length (int): The length of the rectangle to place.

        Returns:
            tuple[int, int]: Coordinates (x, y) of the bottom-left corner, or (-1, -1) 
                            if no valid position is found.
        """
        # Start at the bottom left
        x, y = self.x, self.y

        if self.width < width or self.height < length: return -1, -1

        # If there are defects collapsing the input rectangle
        defects = self.defects_in(x_low = x, x_high = x+width, y_low = y, y_high = y+length)

        if is_vertical: # Start to go up first
            while defects:
                # Go up, and try to find a place
                y = min(defect.y + defect.height for defect in defects)

                # If there are not enough space upwards
                if y + length > self.y + self.height:
                    # Go down, and find the leftmost defect's end
                    y = self.y
                    defects = self.defects_in(x_low = x, x_high = x+width, y_low = y, y_high = y+length)
                    x = min(defect.x + defect.width for defect in defects)

                # Find collapsing defect in the new area
                defects = self.defects_in(x_low = x, x_high = x+width, y_low = y, y_high = y+length)
            
            # If there are not enough space rightwards
            if x + width > self.x + self.width:
                # Return None
                return -1, -1
        
        else: # Start to go right first
            while defects:
                # Go right, and try to find a place
                x = min(defect.x + defect.width for defect in defects)

                # If there are not enough space rightwards
                if x + width > self.x + self.width:
                    # Go left, and find the lowest defect's end
                    x = self.x
                    defects = self.defects_in(x_low = x, x_high = x+width, y_low = y, y_high = y+length)
                    y = min(defect.y + defect.height for defect in defects)

                defects = self.defects_in(x_low = x, x_high = x+width, y_low = y, y_high = y+length)
            
            # If there are not enough space upwards
            if y + length > self.y + self.height:
                # Return None
                return -1, -1
            
        # If we found a place, return it's coordinates
        return x, y


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
    x: int
    y: int
    width: int
    height: int
    type: int
    cut: int
    residual: Residual
    parent: Optional['Node'] = None
    children: List['Node'] = field(default_factory=list)
    been_4_cut: bool = False
    
    # Class-level attribute to automatically assign IDs
    _id_counter: int = field(init=False, repr=False, default=0)
    id: int = field(init=False)

    def __post_init__(self):
        # Automatically assign and increment the ID
        self.id = Node._id_counter
        Node._id_counter += 1
