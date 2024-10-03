from read_input import read_instance

def first_fit_solve(id: str = "A1"):
    """ Solves the glass-cutting problem with a first fit approach"""

    bins, batch = read_instance(id)

    # We should solve it as a tree. 