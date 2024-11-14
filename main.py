import pandas as pd
from solve import first_fit_solve
from os import path
from typing import Optional, List
from classes import Node
from pprint import pprint


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
    csv_file_path = path.join("solutions", f"{id}_solution.csv")
    df.to_csv(csv_file_path, sep=";", index=False)


def run_all(dataset="A"):
    for i in range(1, 21):
        Node.reset_id_counter()
        param = f"{dataset}{i}"
        solution_trees = first_fit_solve(param)
        convert_to_solution_file(solution_trees, param)


def run_one(param="A1"):
    solution_trees = first_fit_solve(param)
    convert_to_solution_file(solution_trees, param)


if __name__ == "__main__":
    # run_one("A2")
    run_all("A")
