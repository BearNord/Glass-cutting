from read_input import read_instance
from pprint import pprint
from classes import Defect, Bin, Item, Stack, Batch, Node, Residual

def first_fit_solve(id: str = "A1"):
    """
    Solves the glass-cutting problem with a first fit approach,
    without rotating the items.
    """
    # trees containts the root nodes of the output
    trees: list[Node] = []  
    
    # Read input
    bins, batch = read_instance(id)

    # Construct the root and the residual
    root, l0_residual = start_new_bin(bins, trees)

    # While there are items to cut
    while batch.stacks: 
        # Take out the first stack from stacks
        current_stack: Stack = batch.stacks.pop(0)
        
        # While there are items in this stack
        while current_stack:
            # Remove first item from current_stack
            current_item: Item = current_stack.sequence.pop(0)

            place_item(current_item, residuals)


            # Try to place it in the bottom left corner
            x, y = l0_residual.find_place(current_item.width, current_item.length)

            # While there is no place start a new bin
            while x == -1:
                residual_to_node(l0_residual, root, -3)
                root, l0_residual = start_new_bin(bins, trees)
                # try to place it in the bottom left corner
                x, y = l0_residual.find_place(current_item.width, current_item.length)
 
            # If there is waste left to the item
            if x != l0_residual.x:
                # Cut that, and make a node from it
                waste = vertical_cut(l0_residual, x)
                residual_to_node(waste, root, -1)
                
            # Cut out the first item in the x coordinate.
            l1_residual = vertical_cut(l0_residual, current_item.width)
            l1_node = residual_to_node(l1_residual, root, -2)
            # Add residual to residual list
            residuals.append(l1_residual)

            # If there is waste under the item
            if y != l0_residual.y:
                # Cut that, and make a node from it
                waste = horizontal_cut(l1_residual, y)
                residual_to_node(waste, l1_node, -1)
            
            # Now we have a residual where we can place the current Item in the left-bottom corner
            # Cut out the first item in the y coordinate.
            l2_residual = horizontal_cut(l1_residual, current_item.length)
            residual_to_node(l2_residual, l1_node, current_item.id)

    # return the list, that contains the root nodes
    return trees


def place_item(current_item: Item, residuals: list[Residual]):
    """
    Try to place item into the last element of residuals
    """
    # Try to place it in the bottom left corner
    residual = residuals[-1]
    x, y = residual.find_place(current_item.width, current_item.length)
    if residual.node is not None:
        residual_to_node(residual, residual.node.parent, -1)

    # While there is no place start a new bin
    while x == -1:
        residual_to_node(residual, root, -3)
        root, residual = start_new_bin(bins, trees)
        # try to place it in the bottom left corner
        x, y = l0_residual.find_place(current_item.width, current_item.length)


def start_new_bin(bins: list[Bin], trees) -> tuple[Node, Residual]:
    # Take out the first bin from bins
    bin: Bin = bins.pop(0)

    # Convert it into a root
    root = Node(
        plate_id = bin.id,
        x = 0,
        y = 0,
        width = bin.width,
        height = bin.height,
        type = -2,
        cut = 0,
        residual = Residual(0, 0, bin.width, bin.height, bin.defects)
    )

    # Make a residual, identical to the first bin.
    residual = Residual(
        x = 0, 
        y = 0, 
        width = bin.width, 
        height = bin.height, 
        defects = bin.defects,
    )
    
    #Append node to tree
    trees.append(root)
    return root, residual


def vertical_cut(original: Residual, width: int) -> Residual:
    """
    Modifies the original residual by creating a vertical cut and returning 
    a new left-side residual.

    Parameters:
        original (Residual): The original residual to be modified.
        width (int): The width of the new left-side residual to be cut.

    Returns:
        Residual: A new residual object representing the left portion of the 
                  original residual after the cut.
    """
    # Construct the new residual
    lower_residual = Residual(
        x = original.x,
        y = original.y,
        width = width,
        height = original.height,
        defects = original.defects_in(original.x, original.x + width,
                                      original.y, original.y + original.height)
    )

    # Update original residual
    original.x += width
    original.width -= width
    original.defects = original.defects_in(original.x, original.x + original.width,
                                            original.y,original.y + original.height)
    
    # Return lower residual
    return lower_residual


def horizontal_cut(original: Residual, height: int) -> Residual:
    """
    Modifies the original residual by creating a horizontal cut and returning 
    a new lower residual.

    Parameters:
        original (Residual): The original residual to be modified.
        height (int): The height of the new lower residual to be cut.

    Returns:
        Residual: A new residual object representing the lower portion of the original 
                  residual after the cut.
    """
     # Construct the new residual
    lower_residual = Residual(
        x = original.x,
        y = original.y,
        width = original.width,
        height = height,
        defects = original.defects_in(original.x, original.x + original.width,
                                      original.y, original.y + height)
    )

    # Update original residual
    original.y += height
    original.height -= height
    original.defects = original.defects_in(original.x, original.x + original.width,
                                            original.y,original.y + original.height)
    
    # Return lower residual
    return lower_residual


def residual_to_node(residual: Residual, parent: Node, type: int) -> Node:
    """
     Converts a Residual into a Node and assigns it as a child of the specified parent node.

    Parameters:
        residual (Residual): The Residual object to convert.
        parent (Node): The parent Node to which the new node will be attached.
        type (int): Type of the node:
            - >= 0: Item ID.
            - -1: Waste.
            - -2: Branch (has children).
            - -3: Residual.

    Returns:
        Node: A new Node object created from the residual.
    """
    node = Node(
        plate_id = parent.plate_id,
        x = residual.x,
        y = residual.y,
        width = residual.width,
        height = residual.height,
        type = type, 
        cut = parent.cut + 1,
        parent = parent
    ) 
    parent.children.append(node)

    return node

    
# NOTE
# We should solve it as a DFS tree.
# How do we implement the tree idea? 
# Should the tree only be a few row of the nodes in a table? (as the output format defines it?) (Porbably shouldn't, it isn't easy or fast to check the remaining glass table size.)