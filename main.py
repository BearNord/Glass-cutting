from solve import first_fit_solve
from classes import Node
from input_output import convert_to_solution_file


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
    # run_one("A13")
    run_all("A")
