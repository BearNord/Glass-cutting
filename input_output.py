import os
import pandas as pd
from classes import Bin, Batch, Item, Stack, Defect, Node, WIDTH_PLATES, HEIGHT_PLATES
from typing import Optional, List


def read_instance(id: str = "A1") -> tuple[list[Bin], Batch]:
    """
    Loads a dataset instance based on the given ID, returning Bin and Batch data.

    Parameters:
        id (str): Dataset instance ID (e.g., "A1"), where the first character
                  indicates the dataset. Defaults to "A1".

    Returns:
        tuple[list[Bin], Batch]: A tuple with:
            - List of Bin objects, each containing defect data.
            - A Batch object with items to cut.
    """
    dataset = id[0]

    # Path to the main datasets folder
    base_path = "datasets"

    # Directory of the dataset
    dataset_path = f"dataset_{dataset}"

    # Instance of the dataset
    batch_file = f"{id}_batch.csv"
    defects_file = f"{id}_defects.csv"

    # Read batches
    batch_file_path = os.path.join(base_path, dataset_path, batch_file)
    batch = read_batch(batch_file_path)

    # Read defects
    defects_file_path = os.path.join(base_path, dataset_path, defects_file)
    bins = read_defects(defects_file_path)

    # returns the dataset
    return bins, batch


def read_batch(file_path: str) -> Batch:
    """
    Generated by ChatGPT
    Read batches.csv and retuns a batch
    """
    # Read the CSV file
    df = pd.read_csv(file_path, sep=";")

    # Create a dictionary to group items by stack
    stacks_dict = {}

    # Iterate over each row in the dataframe
    for _, row in df.iterrows():
        # Create an Item object for each row
        item = Item(
            id=row["ITEM_ID"], width=row["WIDTH_ITEM"], length=row["LENGTH_ITEM"]
        )

        # Add the item to the correct stack
        stack_id = row["STACK"]

        if stack_id not in stacks_dict:
            stacks_dict[stack_id] = []

        stacks_dict[stack_id].append(item)

    # Convert stacks to a list of Stack objects
    stacks = [
        Stack(id=stack_id, sequence=list(items))
        for stack_id, items in stacks_dict.items()
    ]

    # Create a Batch object
    batch = Batch(stacks=stacks)

    # return the batch object with the data
    return batch


def read_defects(file_path: str) -> list[Bin]:
    """
    Generated by ChatGPT
    Read defects.csv and returns a tuple of bins
    """
    # Read the CSV file
    df = pd.read_csv(file_path, sep=";")

    # Dictionary to group defects by Bin (plate)
    bins_dict = {key: [] for key in range(100)}

    # Iterate over each row in the dataframe
    for _, row in df.iterrows():
        # Create a Defect object for each row
        defect = Defect(
            id=int(row["DEFECT_ID"]),
            x=int(float(row["X"])),
            y=int(float(row["Y"])),
            width=int(float(row["WIDTH"])),
            height=int(float(row["HEIGHT"])),
        )

        # Get the bin (plate) ID
        bin_id = int(row["PLATE_ID"])

        # Group defects by bin (plate)
        if bin_id not in bins_dict:
            bins_dict[bin_id] = []

        bins_dict[bin_id].append(defect)

    # Create Bin objects from the grouped defects
    bins = [
        Bin(id=bin_id, width=WIDTH_PLATES, height=HEIGHT_PLATES, defects=defects)
        for bin_id, defects in bins_dict.items()
    ]

    # Now 'bins' contains a list of Bin objects with associated defects
    return bins


def convert_to_solution_file(trees: List[Node], id="A1"):
    """
    Convert a solution of trees into the solution file format.
    Credit: ChatGPT
    """

    def traverse_tree(root: Node):
        # Store the result in a list of dictionaries
        result = []

        def traverse(node: Node, parent_id: Optional[int]):
            # Collect node attributes into a dictionary
            data = {
                "PLATE_ID": node.plate_id,
                "NODE_ID": node.id,
                "X": node.x,
                "Y": node.y,
                "WIDTH": node.width,
                "HEIGHT": node.height,
                "TYPE": node.type,
                "CUT": node.cut,
                "PARENT": parent_id,
            }
            # Append the data to the result list
            result.append(data)

            # Recursively traverse children
            for child in node.children:
                traverse(child, node.id)

        # Start traversal with root node
        traverse(root, None)

        return result

    # Collecting data from all root nodes
    all_nodes_data = []
    for root in trees:
        all_nodes_data.extend(traverse_tree(root))

    # Convert collected data to DataFrame
    df = pd.DataFrame(all_nodes_data)

    # Convert 'PARENT' column to nullable integer type to handle None values without converting to float
    # 'Int64' with a capital 'I' is a nullable integer type
    df["PARENT"] = df["PARENT"].astype("Int64")

    # save to CSV
    csv_file_path = os.path.join("solutions", f"{id}_solution.csv")
    df.to_csv(csv_file_path, sep=";", index=False)