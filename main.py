import os
from solve import first_fit_solve, first_fit_with_rotate, backtrack_solve
from classes import Node
from input_output import convert_to_solution_file
from time import perf_counter

solve = backtrack_solve
output_path = "./checker/checker/instances_checker" #"solutions" 


def run_all(output_path="solutions"):
    run_dataset("A", output_path)
    run_dataset("B", output_path)
    run_dataset("X", output_path)


def run_dataset(dataset="A", output_path="solutions"):
    limit = 21 if dataset == "A" else 16
    for i in range(1, limit):
        Node.reset_id_counter()
        param = f"{dataset}{i}"
        run_one(param, output_path)


def run_one(param="A1", output_path="solutions"):
    output_path = os.path.join(output_path, f"{param}_solution.csv")
    start_time = perf_counter()

    solution_trees = solve(param, 2, True)

    convert_to_solution_file(solution_trees, param, output_path)
    end_time = perf_counter()
    runtime = end_time - start_time
    print(f"\truntime: {runtime:.2f} seconds")
    log_file.append(runtime)


if __name__ == "__main__":
    # output_path = os.path.join("checker", "checker", "instances_checker")
    output_path = "solutions"
    # run_one("A2")
    run_dataset("A", output_path)
