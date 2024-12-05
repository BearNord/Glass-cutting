from solve import first_fit_solve, first_fit_with_rotate, backtrack_solve
from classes import Node
from input_output import convert_to_solution_file
from time import perf_counter

solve = backtrack_solve
output_path = "./checker/checker/instances_checker" #"solutions" 


def run_all(dataset="A", log_file: list = []):
    for i in range(1, 21):
        Node.reset_id_counter()
        param = f"{dataset}{i}"
        run_one(param, log_file)


def run_one(param="A1", log_file:list = []):
    start_time = perf_counter()

    solution_trees = solve(param, 2, True)

    convert_to_solution_file(solution_trees, param)
    end_time = perf_counter()
    runtime = end_time - start_time
    print(f"\truntime: {runtime:.2f} seconds")
    log_file.append(runtime)


if __name__ == "__main__":
    # run_one("A2")
    run_all("A")
