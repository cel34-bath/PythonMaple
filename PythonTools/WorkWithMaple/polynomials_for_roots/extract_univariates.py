import os
import sys

cwd = os.getcwd()
if "Repositories" in cwd:
    initial_directory = cwd.split("Repositories")[0]+"Repositories"
else:
    raise Exception("You're too far from Repositories.")
    
sys.path.append('./') #This means to start looking in the same directory you're running
from WorkWithMaple.UseMaple.use_maple_from_python import create_run_maple_from_python
from WorkWithMaple.CAD.CAD_tools import projection_step_by_maple
#if __name__ == '__main__':
#    import sys
#    sys.path.append(os.getcwd())



def get_polynomials_from_file(file_name):
    '''This function returns the polynomials that are contained in the file 'file_name' '''

    auxiliar_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_file_getpolys.mpl")
    output_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_output.txt")
    maple_output = create_run_maple_from_python(file_location=auxiliar_file, libnames_needed=[os.path.join(initial_directory, "02Tools", "MapleTools")], packages_needed=["TeresoTools"], initializations=[("file_name_maple",file_name)], functions_to_call=[("polynomials_in_file_for_python", ["file_name_maple"], "polynomials")], output_files=[(output_file,"polynomials")], timelimit=30)
    #print("polys in file", maple_output[1])
    return maple_output[1]

def search_univariates(polynomials):
    '''This function is given 'polynomials', a list of polynomials in their matricial form and a list of the univariate polynomials in that list is returned'''

    univariates = []
    for polynomial in polynomials:
        degrees = [monomial[:-1] for monomial in polynomial]
        used_variables = [sum(elem)!=0 for elem in zip(*degrees)]
        if sum(used_variables)==1 and sum([monomial[used_variables.index(1)] for monomial in polynomial])>1: # This is true if polynomial is univariate and if the degree of the polynomial is strictly greater than one
            univariates += [[[monomial[used_variables.index(1)], monomial[-1]] for monomial in polynomial]] # the polynomial is rewritten using only one variable
    return univariates

def recurrent_project_searching_univariates(polynomials, max_nvar: int = 5, max_npolys: int = 200):
    '''This function does a recurrent projection on the polynomials in 'polynomials' while searching for univariates; those univariates are returned as a list.'''
    if polynomials == []: # if an empty list is received just return it
        return []
    elif type(polynomials)==str:
        raise Exception("'polynomials' cannot be defined by a string")

    nvar = len(polynomials[0][0])-1
    npolys = len(polynomials)
    univariates_list = search_univariates(polynomials)
    if nvar > 1 and nvar <= max_nvar and npolys <= max_npolys: # condictions to avoid asking for huge projections
        for variable in range(1,nvar+1):
            new_polynomials = projection_step_by_maple(polynomials, variable, id="_search_univar") ## Would be good to calculate the roots here
            if type(new_polynomials)==list:
                new_univariates_list = recurrent_project_searching_univariates(new_polynomials)
                [univariates_list.append(elem) for elem in new_univariates_list if elem not in univariates_list] # this adds to univariates all the outputs of 'recurrent_project_searching_univariates' that weren't already there
            else:
                print("The projection of ", len(polynomials), " polynomials returned something strange:", new_polynomials)
    return univariates_list