from input_output import read_instance, convert_to_solution_file, draw_loading_bar
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
    WIDTH_PLATES,
    HEIGHT_PLATES,
)
from typing import List, Tuple
from copy import deepcopy, copy
from pprint import pprint


# TODO max distance between 1-cuts: 3500 (except residual)
# TODO must contain at least one 1-cut

# TODO merge place_4_cut and trim
log = True
MAX_WASTE = WIDTH_PLATES * HEIGHT_PLATES * 100


def backtrack_solve(
    id: str = "A1", max_depth: int = 1, extended_waste_calculation=False
):
    print(f"Started backtrack solve algorithm for {id}")
    # trees containts the root nodes of the output
    trees: list[Node] = []

    # Read input
    bins, batch = read_instance(id)

    number_of_items = sum(len(stack.sequence) for stack in batch.stacks)
    placed_items = 0

    # Construct the root and the residual
    current_node = start_new_bin(bins, trees)

    # While there are items to cut
    while batch.stacks:
        min_items: list[Item] = []

        # Solve with backtrack
        id_to_reset = trees[-1].last_descendant().id + 1
        backtrack(
            batch.stacks,
            [],
            0,
            min_items,
            current_node,
            max_depth,
            extended_waste_calculation,
        )
        Node.reset_id_counter(id_to_reset)

        # If no item could be cut
        if not min_items:
            # Finish the previous tree
            make_node(current_node).type = -1
            while current_node.parent != current_node:
                current_node = current_node.parent
                make_node(current_node).type = -1

            # Start new tree
            current_node = start_new_bin(bins, trees)

        # Cut items
        for current_item in min_items:
            for stack in batch.stacks:
                if stack.sequence and stack.sequence[0].id == current_item.id:
                    if log:
                        placed_items += 1
                        draw_loading_bar(number_of_items, placed_items)
                    stack.sequence.pop(0)
                    current_node, _ = place_item(current_item, current_node)

        # Drop empty stacks
        batch.stacks = [stack for stack in batch.stacks if stack.sequence]

    # If the last node is not the root, all nodes to the root should be waste
    while current_node.parent != current_node:
        make_node(current_node).type = -1
        current_node = current_node.parent

    # The last waste is a residual
    make_node(trees[-1]).type = -3

    # Return solution
    print(f"\tFinished first fit solve algorithm for {id}")
    return trees


def first_fit_with_rotate(id: str = "A1"):
    """
    Solves the glass-cutting problem with a first fit approach,
    with occasionally rotating the items.
    """
    print(f"Started first fit solve with rotation algorithm for {id}")
    # trees containts the root nodes of the output
    trees: list[Node] = []

    # Read input
    bins, batch = read_instance(id)

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

            # Save current id
            id_to_continue: int = trees[-1].last_descendant().id + 1

            # Make a copy for each case, so we can try both
            node_for_original = deepcopy(current_node)
            node_for_rotated = deepcopy(current_node)

            # Run the place_item for the original item
            node_for_original, original_success = place_item(
                current_item, node_for_original
            )

            # Make a rotated version of the item, and run place_item on it
            rotated_item = copy(current_item)
            rotated_item.rotate()
            node_for_rotated, rotated_success = place_item(
                rotated_item, node_for_rotated
            )

            # If none of them could be cut
            if not original_success and not rotated_success:
                Node.reset_id_counter(id_to_continue)

                # Finish current bin
                _, _ = place_item(current_item, current_node)
                current_node = start_new_bin(bins, trees)
                id_to_continue = current_node.id + 1

                node_for_original = deepcopy(current_node)
                node_for_rotated = deepcopy(current_node)

                # Run the place_item for the original item
                node_for_original, original_success = place_item(
                    current_item, node_for_original
                )

                # Run place_item for the rotated item
                node_for_rotated, rotated_success = place_item(
                    rotated_item, node_for_rotated
                )

            Node.reset_id_counter(id_to_continue)

            # If only one could be cut
            if original_success and not rotated_success:
                current_node, _ = place_item(current_item, current_node)
            elif rotated_success and not original_success:
                current_node, _ = place_item(rotated_item, current_node)

            # If both could be cut
            elif sum_waste_area(node_for_original.get_root()) <= sum_waste_area(
                node_for_rotated.get_root()
            ):
                current_node, _ = place_item(current_item, current_node)
            else:
                current_node, _ = place_item(rotated_item, current_node)

    # If the last node is not the root, all nodes to the root should be waste
    while current_node.parent != current_node:
        make_node(current_node).type = -1
        current_node = current_node.parent

    # The last waste is a residual
    make_node(trees[-1]).type = -3

    # Return solution
    print(f"\tFinished first fit solve algorithm for {id}")

    return trees


def first_fit_solve(id: str = "A1"):
    """
    Solves the glass-cutting problem with a first fit approach,
    without rotating the items.
    """
    print(f"Started first fit solve algorithm for {id}")
    # trees containts the root nodes of the output
    trees: list[Node] = []

    # Read input
    bins, batch = read_instance(id)

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
    while current_node.parent != current_node:
        make_node(current_node).type = -1
        current_node = current_node.parent

    # The last waste is a residual
    make_node(trees[-1]).type = -3

    # Return solution
    print(f"\tFinished first fit solve algorithm for {id}")
    return trees


def place_item(current_item: Item, current_node: Node) -> Tuple[Node, bool]:
    """
    Places the given item in first fitting position.
    If it can place it, then do it, and return [item's parent, True]
    If can't, then return [root, False]
    """

    # Find place starting from bottom left corner
    x, y = current_node.residual.find_place(
        current_item.width, current_item.length, current_node.cut % 2 == 0
    )

    # If there is no space
    if x == -1:
        # If there is no residual left, we don't need to make a waste from it
        if current_node.residual.width == 0 or current_node.residual.height == 0:
            # If this is the root
            if current_node.parent == current_node:
                return current_node, False
            else:
                return place_item(current_item, current_node.parent)

        # Make a waste node from its residual
        make_node(current_node).type = -1
        # If this is the root
        if current_node.parent == current_node:
            return current_node, False
        else:
            return place_item(current_item, current_node.parent)

    match current_node.cut:
        case 0:  #  1-cut (vertical)

            # If there is a waste to the left
            if x != current_node.residual.x:
                cut_place = x
                # If the cut would be too small
                if x - current_node.residual.x < MIN_1_CUT:
                    cut_place = find_right_to_x(
                        current_node, current_node.residual.x + MIN_1_CUT
                    )

                # If the remaining residual would be too small, go for 2-cut
                if (
                    current_node.residual.x + current_node.residual.width - cut_place
                    < MIN_WASTE
                ):
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
                    current_node,
                    current_node.residual.x + MIN_1_CUT,
                )

            # If the remaining residual would be too small
            if (
                current_node.residual.x + current_node.residual.width - cut_place
                < MIN_WASTE
            ):
                child_node = make_node(current_node)
                return place_item(current_item, child_node)

            child_node = vertical_cut(current_node, cut_place)

            # If the cut was perfect
            if (
                child_node.residual.height == current_item.length
                and child_node.residual.width == current_item.width
            ):
                child_node.type = current_item.id
                return (current_node, True)

            return place_item(current_item, child_node)

        case 1:  #  2-cut (horizontal)

            # If there is a waste
            if y != current_node.residual.y:
                cut_place = y
                # If the cut would be too small
                if y - current_node.residual.y < MIN_2_CUT:
                    cut_place = find_up_to_y(
                        current_node, current_node.residual.y + MIN_2_CUT
                    )

                # If the remaining residual would be too small, go to 3-cut
                if (
                    current_node.residual.y + current_node.residual.height - cut_place
                    < MIN_WASTE
                ):
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

            # If the remaining residual would be too small (in height)
            if (
                current_node.residual.y + current_node.residual.height - cut_place
                < MIN_WASTE
            ):
                child_node = make_node(current_node)
                return place_item(current_item, child_node)

            child_node = horizontal_cut(current_node, cut_place)

            # If the cut was perfect
            if (
                child_node.residual.width == current_item.width
                and child_node.residual.height == current_item.length
            ):
                child_node.type = current_item.id
                return (current_node, True)

            return place_item(current_item, child_node)

        case 2:  # 3-cut (vertical)

            # If there is a waste at left-side
            if x != current_node.residual.x:
                cut_place = x
                # If the waste would be too small
                if x - current_node.residual.x < MIN_WASTE:
                    cut_place = find_right_to_x(
                        current_node, current_node.residual.x + MIN_WASTE
                    )

                if (
                    current_item.length  # If the size is not perfect
                    != current_node.residual.x + current_node.residual.width - cut_place
                    < MIN_WASTE  # and the waste would be too small
                ):
                    # This is a waste
                    make_node(current_node).type = -1
                    return place_item(current_item, current_node.parent)

                # Cut a big enough column, and solve for the remaining part
                waste_node = vertical_cut(current_node, cut_place).type = -1
                return place_item(current_item, current_node)

            # GOAL: perfectly cut the item (which can be perfect from the start)

            cut_place = find_right_to_x(current_node, x + current_item.width)

            # If no vertical cut needed
            if cut_place == current_node.residual.x + current_node.residual.width:
                # Do 4-cut
                child_node = make_node(current_node)
                return place_item(current_item, child_node)

            # If the width is perfect
            if cut_place == x + current_item.width:
                # If the remaining residual would be too small
                if (
                    current_node.residual.x + current_node.residual.width - cut_place
                    < MIN_WASTE
                ):
                    # this is a waste
                    make_node(current_node).type = -1
                    return place_item(current_item, current_node.parent)

                child_node = vertical_cut(current_node, cut_place)

                # If the cut was perfect
                if (
                    child_node.residual.height == current_item.length
                    and child_node.residual.width == current_item.width
                ):
                    child_node.type = current_item.id
                    return (current_node, True)

            else:  # cut was not perfect -> cut a waste column from the left side
                cut_place = find_right_to_x(current_node, x + MIN_WASTE)

                # Check for valid cut
                if (
                    # If after cutting the left part off, the right part is correctly sized
                    current_node.residual.x + current_node.residual.width - cut_place
                    == current_item.width
                    # Or if there is enough for waste after cutting the left part
                    or current_node.residual.x + current_node.residual.width - cut_place
                    >= MIN_WASTE
                ):
                    # Cut off the left (waste) part
                    vertical_cut(current_node, cut_place).type = -1

                    # Try to place the item in the remaining part
                    return place_item(current_item, current_node)

                else:  # there would not be enough space on the right part
                    # This is a waste
                    make_node(current_node).type = -1
                    return place_item(current_item, current_node.parent)

        case 3:  # Instead of 4-cut, do trimming

            if current_item.length == current_node.height:
                current_node.type = current_item.id
                return current_node.parent, True

            current_node, success = trim(current_node, current_item)
            if success:
                return current_node, success
            # Go up until we find usable residuals, and try to cut from it
            while (
                current_node.parent != current_node and current_node.residual.width == 0
            ):
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
    root = Node.create_root(
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
    """
    Trims the given node by specified dimensions and returns a new trimmed node.

    Parameters:
        node (Node): The original node to be trimmed, representing a rectangular area.
        trim_x (int): The amount to reduce the node's width.
        trim_y (int): The amount to reduce the node's height.

    Returns:
        current_node (Node): A new `Node` instance representing the trimmed area of the original node.
    """

    # If not enough waste after cut
    if current_node.residual.height - current_item.length < MIN_WASTE:
        make_node(current_node).type = -1
        return current_node, False

    if current_node.residual.width == current_item.width:
        # Can I place it down?
        if not current_node.residual.has_defect_in(
            current_node.residual.x,
            current_node.residual.x + current_node.residual.width,
            current_node.residual.y,
            current_node.residual.y + current_item.length,
        ):
            # do horizontal cut, and down is suitable
            horizontal_cut(current_node, current_node.y + current_item.length).type = (
                current_item.id
            )
            make_node(current_node).type = -1

            return current_node.parent, True

        # Can I place it up?
        elif not current_node.residual.has_defect_in(
            current_node.residual.x,
            current_node.residual.x + current_node.residual.width,
            current_node.residual.y
            + current_node.residual.height
            - current_item.length,
            current_node.residual.y + current_node.residual.height,
        ):
            # do horizontal cut, and up is suitable
            horizontal_cut(
                current_node, current_node.y + current_node.height - current_item.length
            ).type = -1
            make_node(current_node).type = current_item.id

            return current_node.parent, True

    # Cannot place item here with a 4-cut
    make_node(current_node).type = -1
    return current_node.parent, False


def find_right_to_x(current_node: Node, cut_place: int):
    """
    Finds the first valid x-coordinate for a cut in the given node's residual area, avoiding defects.

    Parameters:
        current_node (Node): The node with the residual area to evaluate for a cut.
        cut_place (int): Initial x-coordinate for the cut attempt.

    Returns:
        cut_place (int) : The x-coordinate of the first defect-free cutting location.
    """
    # Check if there are defects in our cut
    defects = current_node.residual.defects_in(
        cut_place - 1,
        cut_place + 1,
        current_node.residual.y,
        current_node.residual.y + current_node.residual.height,
    )

    # Filter out defects that start or end at cut_place #TODO test
    defects = [
        defect
        for defect in defects
        if not (defect.x == cut_place or defect.x + defect.width == cut_place)
    ]

    # Move to the right until we can cut
    while defects:
        cut_place = max(defect.x + defect.width for defect in defects)
        defects = current_node.residual.defects_in(
            cut_place - 1,
            cut_place + 1,
            current_node.residual.y,
            current_node.residual.y + current_node.residual.height,
        )

        # Filter out defects that start or end at cut_place
        defects = [
            defect
            for defect in defects
            if not (defect.x == cut_place or defect.x + defect.width == cut_place)
        ]

    return cut_place


def find_up_to_y(current_node: Node, cut_place: int):
    """
    Finds the first valid y-coordinate for a cut in the given node's residual area, avoiding defects.

    Parameters:
        current_node (Node): The node with the residual area to evaluate for a cut.
        cut_place (int): Initial y-coordinate for the cut attempt.

    Returns:
        cut_place (int) : The y-coordinate of the first defect-free cutting location.
    """
    # Check if there are defects in our cut
    defects = current_node.residual.defects_in(
        current_node.residual.x,
        current_node.residual.x + current_node.residual.width,
        cut_place - 1,
        cut_place + 1,
    )

    # Filter out defects that start or end at cut_place # TODO test
    defects = [
        defect
        for defect in defects
        if not (defect.y == cut_place or defect.y + defect.height == cut_place)
    ]

    # Move to the right until we can cut
    while defects:
        cut_place = max(defect.y + defect.height for defect in defects)
        defects = current_node.residual.defects_in(
            current_node.residual.x,
            current_node.residual.x + current_node.residual.width,
            cut_place - 1,
            cut_place + 1,
        )

        # Filter out defects that start or end at cut_place
        defects = [
            defect
            for defect in defects
            if not (defect.y == cut_place or defect.y + defect.height == cut_place)
        ]

    return cut_place


def sum_waste_area(root: Node) -> int:
    """
    Calculates the total area of waste nodes in a subtree using depth-first search (DFS).

    Parameters:
        root (Node): The root of the subtree.

    Returns:
        int: The total waste area, computed as the sum of `height * width` for all waste nodes.
    """

    # DFS or recursive traversal function to sum areas of waste nodes
    def dfs(node: Node) -> int:
        total_area = 0
        if node.type == -1:  # It's a waste node
            total_area += node.height * node.width

        # Traverse the children
        for child in node.children:
            total_area += dfs(child)

        return total_area

    # Start DFS from the root node
    return dfs(root)


def backtrack(
    stacks: list[Stack],
    item_list: list[Item],
    current_depth: int,
    min_items: list[Item],
    current_node: Node,
    max_depth: int = 1,
    extended_waste_calculation=False,
) -> int:
    # If we are too deep, then calculate the waste area and return
    if current_depth == max_depth:
        waste = sum_waste_area(current_node.get_root())

        if extended_waste_calculation:
            # Sum the wastes up to the root
            temp_node = current_node
            while temp_node.parent != temp_node:
                waste += temp_node.residual.width * temp_node.residual.height
                temp_node = temp_node.parent

            # If the stack list is empty
            if not stacks:
                root = current_node.get_root()
                # the residual node is not a waste
                waste -= root.residual.width * root.residual.height

        # return waste
        return waste

    # smallest_waste = infinity
    smallest_waste = MAX_WASTE

    # go through all possible items
    for stack_ind in range(len(stacks)):

        # copy the stacks
        new_stacks = deepcopy(stacks)
        current_item = new_stacks[stack_ind].sequence.pop(0)
        if not new_stacks[stack_ind].sequence:
            new_stacks.pop(stack_ind)

        item_list.append(current_item)

        # Make a copy for rotated and original case, so we can try both
        node_for_original = deepcopy(current_node)
        node_for_rotated = deepcopy(current_node)

        # Run the place_item for the original item
        node_for_original, original_success = place_item(
            current_item, node_for_original
        )

        # Make a rotated version of the item, and run place_item on it
        rotated_item = copy(current_item)
        rotated_item.rotate()
        node_for_rotated, rotated_success = place_item(rotated_item, node_for_rotated)

        # If the original could be cut
        if original_success:
            orig_waste = backtrack(
                new_stacks,
                item_list,
                current_depth + 1,
                min_items,
                node_for_original,
                max_depth,
                extended_waste_calculation,
            )
            if smallest_waste > orig_waste:
                smallest_waste = orig_waste
                min_items.clear()
                min_items.extend(item_list)  # Update the list in place
                # min_items = deepcopy(item_list)

        # If the rotated could be cut
        if rotated_success:
            item_list[-1] = rotated_item
            rotated_waste = backtrack(
                new_stacks,
                item_list,
                current_depth + 1,
                min_items,
                node_for_rotated,
                max_depth,
                extended_waste_calculation,
            )
            if smallest_waste > rotated_waste:
                smallest_waste = rotated_waste
                min_items.clear()
                min_items.extend(item_list)  # Update the list in place
                # min_items = deepcopy(item_list)

        item_list.pop()

    # If there was no placeable item
    if smallest_waste == MAX_WASTE:
        waste = sum_waste_area(current_node.get_root())

        # Sum the wastes up to the root
        temp_node = current_node
        waste += temp_node.residual.width * temp_node.residual.height
        while temp_node.parent != temp_node:
            temp_node = temp_node.parent
            waste += temp_node.residual.width * temp_node.residual.height

        # If the stack list is originally empty
        if not stacks:
            root = current_node.get_root()
            # the residual node is not a waste
            waste -= root.residual.width * root.residual.height

        return waste

    return smallest_waste
