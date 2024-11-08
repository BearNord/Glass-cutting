from read_input import read_instance
from classes import (
    Bin,
    Item,
    Stack,
    Node,
    Residual,
    Place,
    MIN_1_CUT,
    MIN_2_CUT,
    MIN_WASTE,
)
from typing import List, Tuple
from pprint import pprint


# TODO max distance between 1-cuts: 3500 (except residual)
# TODO must contain at least one 1-cut

# TODO (Optional) Don't do waste cut for 1-cut

log = False


def first_fit_solve(id: str = "A1"):
    """
    Solves the glass-cutting problem with a first fit approach,
    without rotating the items.
    """
    print("Started first fit solve algorithm")
    # trees containts the root nodes of the output
    trees: list[Node] = []

    # Read input
    bins, batch = read_instance(id)
    # pprint(bins[:7])

    # Construct the root and the residual
    current_node = start_new_bin(bins, trees)

    # While there are items to cut
    while batch.stacks:
        # Take out the first stack from stacks
        current_stack: Stack = batch.stacks.pop(0)

        # While there are items in this stack
        while current_stack.sequence:
            # Remove first item from current_stack
            current_item: Item = current_stack.sequence.pop(0)

            if log == True:
                print(
                    f"Trying to place item: {current_item.id} into bin {current_node.plate_id}"
                )
            current_node, success = place_item(current_item, current_node)
            while not success:
                current_node = start_new_bin(bins, trees)
                current_node, success = place_item(current_item, current_node)

    # If the last node is not the root, all nodes to the root should be waste
    while current_node.parent is not None:
        make_node(current_node).type = -1
        current_node = current_node.parent

    # The last waste is a residual
    make_node(trees[-1]).type = -3

    # Return solution
    return trees


def place_item(current_item: Item, current_node: Node) -> Tuple[Node, bool]:
    """
    Places the given item in first fitting position.
    If it can place it, then do it, and return [current_node, True]
    If can't, then return [root, False]
    """

    # Find place starting from bottom left corner
    x, y = current_node.residual.find_place(
        current_item.width, current_item.length, current_node.cut % 2 == 0
    )

    # If there is no space
    if x == -1:
        # Make a waste node from its residual
        make_node(current_node).type = -1
        # If this is the root
        if current_node.parent is None:
            return current_node, False
        else:
            return place_item(current_item, current_node.parent)

    match current_node.cut:
        case 0:  #  1-cut (vertical)
            # If there is a waste
            if x != current_node.residual.x:
                cut_place = x
                # If the waste is too small
                if x - current_node.residual.x < MIN_WASTE:
                    cut_place = find_right_to_x(
                        current_node, current_node.residual.x + MIN_WASTE
                    )

                # If the remaining residual would be too small, go for 2-cut
                if current_node.residual.width - cut_place < MIN_WASTE:
                    child_node = make_node(current_node)
                    return place_item(current_item, child_node)

                # Cut a big enough column, and solve for the remaining part
                waste_node = vertical_cut(current_node, cut_place)
                waste_node.type = -1
                return place_item(current_item, current_node)

            cut_place = find_right_to_x(current_node, x + current_item.width)

            # If the cut would be smaller than the minimum
            if cut_place - current_node.residual.x < MIN_1_CUT:
                # Find the smallest x were we can cut
                cut_place = find_right_to_x(
                    current_node, current_node.residual.x + MIN_1_CUT
                )

            # If the remaining residual would be too small
            if (
                current_node.residual.x + current_node.residual.width - cut_place
                < MIN_WASTE
            ):
                child_node = make_node(current_node)
                return place_item(current_item, child_node)

            child_node = vertical_cut(current_node, cut_place)
            if child_node.residual.height == current_item.length:
                child_node.type = current_item.id
                return (current_node, True)

        case 1:  #  2-cut (horizontal)
            # If there is a waste
            if y != current_node.residual.y:
                cut_place = y
                # If the waste is too small
                if y - current_node.residual.y < MIN_WASTE:
                    cut_place = find_up_to_y(
                        current_node, current_node.residual.y + MIN_WASTE
                    )

                # If the remaining residual would be too small, go to 3-cut
                if current_node.residual.height - cut_place < MIN_WASTE:
                    child_node = make_node(current_node)
                    return place_item(current_item, child_node)

                # Cut a big enough column, and solve for the remaining part
                waste_node = horizontal_cut(current_node, cut_place)
                waste_node.type = -1
                return place_item(current_item, current_node)

            cut_place = find_up_to_y(current_node, y + current_item.length)

            # If the cut would be smaller than the minimum
            if cut_place - current_node.residual.y < MIN_2_CUT:
                # Find the smallest x where we can cut
                cut_place = find_up_to_y(
                    current_node, current_node.residual.x + MIN_2_CUT
                )

            # If the remaining residual would be too small
            if (
                current_node.residual.y + current_node.residual.height - cut_place
                < MIN_WASTE
            ):
                child_node = make_node(current_node)
                return place_item(current_item, child_node)

            child_node = horizontal_cut(current_node, cut_place)
            if child_node.residual.width == current_item.width:
                child_node.type = current_item.id
                return (current_node, True)

        case 2:  # 3-cut (vertical)

            # If there is a waste
            if x != current_node.residual.x:
                cut_place = x
                # If the waste is too small
                if x - current_node.residual.x < MIN_WASTE:
                    cut_place = find_right_to_x(
                        current_node, current_node.residual.x + MIN_WASTE
                    )

                # If the remaining residual would be too small, go for trimming
                if current_node.residual.width - cut_place < MIN_WASTE:
                    child_node = make_node(current_node)
                    return place_item(current_item, child_node)

                # Cut a big enough column, and solve for the remaining part
                waste_node = vertical_cut(current_node, cut_place)
                waste_node.type = -1
                return place_item(current_item, current_node)

            cut_place = find_right_to_x(current_node, x + current_item.width)

            # If the remaining residual would be too small
            if (
                current_node.residual.x + current_node.residual.width - cut_place
                < MIN_WASTE
            ):
                child_node = make_node(current_node)
                return place_item(current_item, child_node)

            child_node = vertical_cut(current_node, cut_place)
            if child_node.residual.height == current_item.length:
                child_node.type = current_item.id
                return (current_node, True)

        case 3:  # Instead of 4-cut, do trimming
            current_node, success = trim(current_node, current_item)
            if success:
                return current_node, success
            # Go up until we find usable residuals, and try to cut from it
            while current_node.parent is not None and current_node.residual.width == 0:
                current_node = current_node.parent
            if current_node.residual.width != 0:
                return place_item(current_item, current_node)
            # If haven't found, than this item won't fit in this bin
            return current_node, False

    return place_item(current_item, child_node)


def start_new_bin(bins: list[Bin], trees: List[Node]) -> Node:
    """
    Creates a new root node from the first bin in `bins` and adds it to `trees`.

    Removes the first bin from `bins`, initializes it as a root node with its dimensions
    and defects, and appends it to the `trees` list.

    Parameters:
        bins (list[Bin]): List of available bins, from which the first bin is used.
        trees (list): List of tree structures, to which the new root node is added.

    Returns:
        Node: The created root node representing the bin.
    """
    # Take out the first bin from bins
    bin = bins.pop(0)

    # Convert it into a root
    root = Node(
        plate_id=bin.id,
        x=0,
        y=0,
        width=bin.width,
        height=bin.height,
        type=-2,
        cut=0,
        residual=Residual(0, 0, bin.width, bin.height, bin.defects),
    )

    # Append node to tree
    trees.append(root)
    return root


def vertical_cut(current_node: Node, x: int) -> Node:
    """
    Modifies the original node by creating a vertical cut and returning
    a new node with the right parameters.

    Parameters:
        original (Node): The original node to be modified.
        x (int): The coordinate to cut at.

    Returns:
        child_node (Node): A new node object representing the left portion of the
        original residual after the cut.
    """
    # Construct the new Node
    child_node = Node(
        plate_id=current_node.plate_id,
        x=current_node.residual.x,
        y=current_node.residual.y,
        width=x - current_node.residual.x,
        height=current_node.residual.height,
        type=-2,
        cut=current_node.cut + 1,
        parent=current_node,
        residual=Residual(
            x=current_node.residual.x,
            y=current_node.residual.y,
            width=x - current_node.residual.x,
            height=current_node.residual.height,
            defects=current_node.residual.defects_in(
                current_node.residual.x,
                x,
                current_node.residual.y,
                current_node.residual.y + current_node.residual.height,
            ),
        ),
    )
    current_node.children.append(child_node)

    # Update the current_node residual
    current_node.residual.x = x
    current_node.residual.width -= child_node.width
    current_node.residual.defects = current_node.residual.defects_in(
        current_node.residual.x,
        current_node.residual.x + current_node.residual.width,
        current_node.residual.y,
        current_node.residual.y + current_node.residual.height,
    )

    return child_node


def horizontal_cut(current_node: Node, y: int) -> Node:
    """
    Modifies the original node by creating a horizontal cut and returning
    a new node with the appropriate parameters.

    Parameters:
        current_node (Node): The original node to be modified.
        y (int): The coordinate to cut at.

    Returns:
        child_node (Node): A new node object representing the top portion of the
        original residual after the cut.
    """
    # Construct the new Node
    child_node = Node(
        plate_id=current_node.plate_id,
        x=current_node.residual.x,
        y=current_node.residual.y,
        width=current_node.residual.width,
        height=y - current_node.residual.y,
        type=-2,
        cut=current_node.cut + 1,
        parent=current_node,
        residual=Residual(
            x=current_node.residual.x,
            y=current_node.residual.y,
            width=current_node.residual.width,
            height=y - current_node.residual.y,
            defects=current_node.residual.defects_in(
                current_node.residual.x,
                current_node.residual.x + current_node.residual.width,
                current_node.residual.y,
                y,
            ),
        ),
    )
    current_node.children.append(child_node)

    # Update the current_node residual
    current_node.residual.y = y
    current_node.residual.height -= child_node.height
    current_node.residual.defects = current_node.residual.defects_in(
        current_node.residual.x,
        current_node.residual.x + current_node.residual.width,
        current_node.residual.y,
        current_node.residual.y + current_node.residual.height,
    )

    return child_node


def place_4_cut(node: Node, item: Item) -> Place:
    """
    Decides where an item can be placed for a 4-cut.

    Parameters:
        - node (Node): The node where there is a 4-cut.
        - item (Item): The item to place.

    Returns:
        - Place: An enum value indicating the suitable placement direction:
            - Place.LEFT: Indicates a vertical cut; left is suitable for the item.
            - Place.RIGHT: Indicates a vertical cut; right is suitable for the item.
            - Place.DOWN: Indicates a horizontal cut; down is suitable for the item.
            - Place.UP: Indicates a horizontal cut; up is suitable for the item.
            - Place.NONE: Indicates that the item cannot be placed.
    """

    if node.residual.height == item.length:
        # Can I place it left?
        if not node.residual.has_defect_in(
            node.residual.x,
            node.residual.y,
            node.residual.x + item.width,
            node.residual.y + node.residual.height,
        ):
            return Place.LEFT

        # Can I place it right?
        elif not node.residual.has_defect_in(
            node.residual.x + node.residual.width - item.width,
            node.residual.y,
            node.residual.x + node.residual.width,
            node.residual.y + node.residual.height,
        ):
            return Place.RIGHT

    if node.residual.width == item.width:
        # Can I place it down?
        if not node.residual.has_defect_in(
            node.residual.x,
            node.residual.y,
            node.residual.x + node.residual.width,
            node.residual.y + item.length,
        ):
            return Place.DOWN

        # Can I place it up?
        elif not node.residual.has_defect_in(
            node.residual.x,
            node.residual.y + node.residual.height - item.length,
            node.residual.x + node.residual.width,
            node.residual.y + node.residual.height,
        ):
            return Place.UP

    return Place.NONE


def make_node(current_node: Node) -> Node:
    """
    Converts the remaining residual of the current node into a node.

    Creates a new child node marked as "branch node" from the current node's residual area,
    then clears the residual properties of the current node to indicate no remaining usable area.

    Parameters:
        current_node (Node): The node with residual area to be converted into waste.

    Returns:
        None
    """
    # Make waste node
    child_node = Node(
        plate_id=current_node.plate_id,
        x=current_node.residual.x,
        y=current_node.residual.y,
        width=current_node.residual.width,
        height=current_node.residual.height,
        type=-2,
        cut=current_node.cut + 1,
        parent=current_node,
        residual=Residual(
            x=current_node.residual.x,
            y=current_node.residual.y,
            width=current_node.residual.width,
            height=current_node.residual.height,
            defects=current_node.residual.defects,
        ),
    )
    current_node.children.append(child_node)

    # Clear the residual of the current node
    current_node.residual.x = current_node.x + current_node.width
    current_node.residual.y = current_node.y + current_node.height
    current_node.residual.width = 0
    current_node.residual.height = 0
    current_node.residual.defects = []

    return child_node


def trim(current_node: Node, current_item: Item) -> Tuple[Node, bool]:

    # Trimming: With 1 cut (vertical or horizontal) create 2 part: 1 item and 1 waste (or 2 items)
    place = place_4_cut(current_node, current_item)

    if place in (Place.LEFT, Place.RIGHT):
        # If not enough waste after cut
        if (
            current_node.residual.x + current_node.residual.width - current_item.width
            < MIN_WASTE
        ):
            make_node(current_node).type = -1
            return current_node, False
    elif place in (Place.UP, Place.DOWN):
        # If not enough waste after cut
        if (
            current_node.residual.y + current_node.residual.height - current_item.length
            < MIN_WASTE
        ):
            make_node(current_node).type = -1
            return current_node, False

    if place == Place.LEFT:
        # do vertical cut, and left side is suitable
        vertical_cut(current_node, current_node.x + current_item.width).type = (
            current_item.id
        )
        make_node(current_node).type = -1
    elif place == Place.RIGHT:
        # do vertical cut, and right side is suitable
        vertical_cut(
            current_node,
            current_node.residual.x + current_node.residual.width - current_item.width,
        ).type = -1
        make_node(current_node).type = current_item.id
    elif place == Place.DOWN:
        # do horizontal cut, and down is suitable
        horizontal_cut(current_node, current_node.y + current_item.length).type = (
            current_item.id
        )
        make_node(current_node).type = -1
    elif place == Place.UP:
        # do horizontal cut, and up is suitable
        horizontal_cut(
            current_node, current_node.y + current_node.height - current_item.length
        ).type = -1
        make_node(current_node).type = current_item.id
    else:
        # Cannot place item here with a 4-cut
        make_node(current_node).type = -1
        if current_node.parent is not None:
            return current_node.parent, False
    if current_node.parent is not None:
        return current_node.parent, True

    # only for typehinting... (never happens.... or at least it shouldn't)
    return current_node, False


def find_right_to_x(current_node: Node, cut_place: int):
    """
    Finds the first place on the x-axis where we can cut (not cutting through a defect).
    """
    # Check if there are defects in our cut
    defects = current_node.residual.defects_in(
        cut_place - 1,
        cut_place + 1,
        current_node.residual.y,
        current_node.residual.y + current_node.residual.height,
    )

    # Move to the right until we can cut
    while defects:
        cut_place = max(defect.x + defect.width for defect in defects)
        defects = current_node.residual.defects_in(
            cut_place - 1,
            cut_place + 1,
            current_node.residual.y,
            current_node.residual.y + current_node.residual.height,
        )

    return cut_place


def find_up_to_y(current_node: Node, cut_place: int):
    """
    Finds the first place on the x-axis where we can cut (not cutting through a defect).
    """
    # Check if there are defects in our cut
    defects = current_node.residual.defects_in(
        current_node.residual.x,
        current_node.residual.x + current_node.residual.width,
        cut_place - 1,
        cut_place + 1,
    )

    # Move to the right until we can cut
    while defects:
        cut_place = max(defect.y + defect.height for defect in defects)
        defects = current_node.residual.defects_in(
            current_node.residual.x,
            current_node.residual.x + current_node.residual.width,
            cut_place - 1,
            cut_place + 1,
        )

    return cut_place
