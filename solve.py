from read_input import read_instance
from pprint import pprint

def first_fit_solve(id: str = "A1"):
    """ Solves the glass-cutting problem with a first fit approach"""

    bins, batch = read_instance(id)

    

    # We should solve it as a DFS tree.

    # How do we implement the tree idea? 
    # Should the tree only be a few row of the nodes in a table? (as the output format defines it?) (Porbably shouldn't, it isn't easy or fast to check the remaining glass table size.)