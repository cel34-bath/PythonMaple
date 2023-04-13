import os
import sys

this_file_directory = os.path.dirname(os.path.abspath(__file__))
if "Repositories" in this_file_directory:
    initial_directory = (this_file_directory.split("Repositories")[0]
                         + "Repositories")
else:
    raise Exception("You're too far from Repositories.")

sys.path.append(os.path.join(initial_directory, '02Tools', 'PythonTools'))
from WorkWithMaple.UseMaple.use_maple_from_python import create_run_maple_from_python


def CAD_by_maple(polynomials, variable_order, timeout: int = 30):  # noqa N802
    """
    Call Maple to do a CAD.

    CAD of the polynomials in matricial form in 'polynomials'
    using the variable order described in 'variable_order'.
    It will return the time taken by Maple to create the CAD object
    and also all the polynomials generated in the projection phase.
    """
    auxiliar_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_CAD_aux.mpl")
    output_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_CAD_output.txt")
    # file_to_read = os.path.join(initial_directory, "02Tools", "MapleTools", "CAD_tools", "CAD_tools_maple.mpl")

    aux = create_run_maple_from_python(
        file_location=auxiliar_file,
        libnames_needed=[os.path.join(initial_directory, "02Tools",
                         "MapleTools")],
        packages_needed=["TeresoTools"],
        initializations=[("polynomials_python", polynomials),
                         ("variable_order", variable_order)],
        functions_to_call=[("CAD_from_python", ["polynomials_python",
                           "variable_order"], "projection_lifting")],
        output_files=[(output_file, "projection_lifting")],
        timelimit=timeout
        )
    if aux[0] == 2:
        timing = "Time over"
        proj_polys = []
        ncells = "Unknown "+str(timeout)
        print("Timeover: ", aux[0])
    elif aux[0] == 0:
        timing = "Time over"
        proj_polys = []
        ncells = "Unknown "+str(timeout)
        with open(auxiliar_file, 'r') as f:
            print(f.read())
        print("Try to see why the previous code did not run.")
    elif aux[0] == 1:
        print("aux: ", aux)
        timing = aux[1]  # time needed to generate the CAD
        proj_polys = aux[2][0]  # a set of sets of all the projected polynomials on each step
        ncells = aux[2][1]  # a set of sets of the number of cells by dimension on each step of the lifting
    return timing, proj_polys, ncells
    

def recurrent_project(polynomials,
                      max_nvar: int = 5,
                      max_npolys: int = 10000,
                      return_for_heuristics: bool = False
                      ):
    '''This function does all possible recurrent projection on the polynomials in 'polynomials' expressed in matricial form. The order of the possible variable orderings is the same as in itertools.permutations()
    If return_for_heuristics is True then some information on the degrees of the projected polynomials and the timings of each projection are returned'''
    if polynomials == []: # if an empty list is received just return it
        return [[[]]], [[0]], [[0]]
    elif type(polynomials)==str:
        raise Exception("'polynomials' cannot be defined by a string")

    nvar = len(polynomials[0][0])-1
    npolys = len(polynomials)
    all_projections = [[polynomials]]
    relevant_degrees = [[sum([degree(polynomial, 0) for polynomial in polynomials])]]
    proj_timings = [[0]]
    if nvar <= max_nvar and npolys <= max_npolys: # condictions to avoid asking for huge projections
        if nvar > 1: # if there is something left to project
            all_projections = [] # will contain a list of all the possible projections for the different variable orderings
            relevant_degrees = [] # will contain a list of the sum of the degrees of the polynomials with resepect to the variable that is being projected
            proj_timings = []
            for variable in range(1,nvar+1): # Maple asks for variables described using an integer (>0)
                if not return_for_heuristics:
                    new_polynomials = projection_step_by_maple(polynomials, variable)
                else:
                    new_polynomials, proj_timing = projection_step_by_maple(polynomials, variable, return_proj_timing=True) 
                variable_degree = sum([degree(polynomial, variable-1) for polynomial in polynomials])
                if type(new_polynomials)==list:
                    if not return_for_heuristics:
                        new_projections = recurrent_project(new_polynomials)
                    else:
                        new_projections, new_relevant_degrees, new_proj_timings = recurrent_project(new_polynomials, return_for_heuristics = True)
                        relevant_degrees += [[variable_degree] + new_relevant_degree for new_relevant_degree in new_relevant_degrees] # this ensures that the degree in this stage is added properly to the list
                        proj_timings += [[proj_timing] + new_proj_timing for new_proj_timing in new_proj_timings]
                    all_projections += [[polynomials] + new_projection for new_projection in new_projections] # this ensures that the polynomials in this stage are added properly to the list
                else: # if the projection does not finish on time we make sure this order is not chosen
                    print("The projection of ", len(polynomials), " polynomials returned something strange:", new_polynomials)
                    all_projections += [[[[[999999]*(nvar+1)]]]]
                    relevant_degrees += [[999999]]
                    proj_timings += [[999999]]
    if not return_for_heuristics:
        # if we are interested in heuristics we also return the relevant degrees (for heuristics)
        return all_projections
    else:
        return all_projections, relevant_degrees, proj_timings

def projection_step_by_maple(polynomials, variable, timeout = 10, id="", return_proj_timing:bool=False):
    '''This function will do a projection step of the polynomials in matricial form in 'polynomials' over the variable 'variable' '''

    auxiliar_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_file_proj"+id+".mpl")
    output_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_output"+id+".txt")
    aux = create_run_maple_from_python(file_location=auxiliar_file, libnames_needed=[os.path.join(initial_directory, "02Tools", "MapleTools")], packages_needed=["TeresoTools"],  initializations=[("polynomials_python",polynomials)], functions_to_call=[("projection_step_from_python", ["polynomials_python",str(variable)], "proj_polys")] ,output_files=[(output_file,"proj_polys")], timelimit=timeout)
    new_polynomials = aux[2] # create_run_maple_from_python returns a vector containing the time in position 0 and the desired outputs after
    timing = aux[1]

    if new_polynomials == "proj_polys":
        with open(auxiliar_file, 'r') as f:
            print(f.read())
    if return_proj_timing:
        return new_polynomials, timing
    else:
        return new_polynomials 

def degree(polynomial:list, variable:int):
    '''Computes the degree of a polynomial in matricial form with respect to a given variable.'''
    return max([monomial[variable] for monomial in polynomial]) # if out of range means variable is too big

def degree_in_list(poly_list, variable:int):
    '''Computes the degree of the product of the polynomials in matricial form with respect to a given variable.'''
    return prod([degree(polynomial, variable) for polynomial in poly_list])

def first_vector_is_smaller_or_equal(vec1, vec2):
    '''
    If the vector that describes vec1 is smaller than vec2 True is returned, else False.
    If they are equal True is returned.
    vec1 and vec2 have the same length.
    '''
    for elem1, elem2 in zip(vec1, vec2):
        if elem1 < elem2:
            return True
        elif elem1 > elem2:
            return False
    return True

def remove_repeated(problems):       
    unique_problems = []        
    unique_ncells = []
    for problem in problems:
        if problem.get_ncells() not in unique_ncells:                     
            unique_problems.append(problem)                
            unique_ncells.append(problem.get_ncells())
    return unique_problems