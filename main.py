from solve import first_fit_solve, first_fit_with_rotate
from classes import Node
from input_output import convert_to_solution_file

solve = first_fit_with_rotate


def run_all(dataset="A"):
    for i in range(1, 21):
        Node.reset_id_counter()
        param = f"{dataset}{i}"
        solution_trees = solve(param)
        convert_to_solution_file(solution_trees, param)


def run_one(param="A1"):
    solution_trees = solve(param)
    convert_to_solution_file(solution_trees, param)


if __name__ == "__main__":
    run_one("A5")
    # run_all("A")
