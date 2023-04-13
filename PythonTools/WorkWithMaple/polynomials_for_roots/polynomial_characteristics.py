import os
import sys
from collections import Counter

cwd = os.getcwd()
if "Repositories" in cwd:
    initial_directory = cwd.split("Repositories")[0]+"Repositories"
else:
    raise Exception("You're too far from Repositories.")
    
sys.path.append('./') #This means to start looking in the same directory you're running
from WorkWithMaple.UseMaple.use_maple_from_python import create_run_maple_from_python
#if __name__ == '__main__':
#    import sys
#    sys.path.append(os.getcwd())



def number_of_roots_by_maple(polynomials, timeout = 5):
    '''This function will return a list of the number of roots of the list of univatiate polynomials given in matricial form in 'po
    lynomials' '''

    if polynomials == []:
        return []
    
    auxiliar_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_file_nroots.mpl")
    output_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_output.txt")
    aux = create_run_maple_from_python(file_location=auxiliar_file, libnames_needed=[os.path.join(initial_directory, "02Tools", "MapleTools")], packages_needed=["TeresoTools"], initializations=[("polynomials_python",polynomials)], functions_to_call=[("number_of_roots_from_python", ["polynomials_python"], "nroots")] ,output_files=[(output_file,"nroots")], timelimit=timeout)
    nroots = aux[1] # create_run_maple_from_python returns a vector containing the time in position 0 and the desired outputs after
    #print("\n roots of:", polynomials, "are", nroots)
    if type(nroots)==str:
        print("No enough time to calculate the roots. Number of polys: ", len(polynomials))
        nroots = ["Unknown nroots" for poly in polynomials]
    return nroots

def characteristics_univariate_polynomials(polynomials, folder):
    '''This function creates a list of lists that includes the univariate polynomials in 'polynomials' and some of their characteristics'''

    nroots = number_of_roots_by_maple(polynomials)
    if type(nroots)==str:
        print("No se han podido calcular las raices")
    return [[polynomial, folder, max([monomial[0] for monomial in polynomial]), len(polynomial), nroot] for polynomial,nroot in zip(polynomials,nroots)] # this is a list of lists containing a polynomial, the folder it was found in, the degree, the number of terms and the number of roots it has.

def characteristics_multivariate_polynomials(polynomials, folder):
    '''This function creates a list that includes the polynomials in 'polynomial' and lists of some of their characteristics'''
    nvariables = [len(polynomial[0])-1 for polynomial in polynomials]
    used_variables = [[int(sum(elem)!=0) for elem in zip(*[monomial[:-1] for monomial in polynomial])] for polynomial in polynomials]
    #coefficients = [monomial[-1] for polynomial in polynomials for monomial in polynomial]
    #exponents = [elem for polnomialy in polynomials for monomial in polnomialy for elem in monomial[:-1]]
    maxdegrees = [max([sum(monomial[:-1]) for monomial in polynomial]) for polynomial in polynomials]
    nterms = [len(polynomial) for polynomial in polynomials]
    return [[polynomials, folder, nvariables, used_variables, maxdegrees, nterms]]

def number_of_terms(polynomial:list=[]):
    '''This function counts the number of terms of a polynomial given in matricial form'''

    degrees = [monomial[:-1] for monomial in polynomial]
    unique_degrees = []
    coefficients = []
    for monomial in polynomial:
        if monomial[:-1] not in unique_degrees:
            unique_degrees.append(monomial[:-1])
            coefficients.append(monomial[-1])
        else:
            coefficients[unique_degrees.index(monomial[:-1])] += monomial[-1]

    return len([coeff for coeff in coefficients if coeff!=0])

polynomial = [[3,1,2,4],[4,1,6,3],[5,3,1,5],[3,1,2,2],[4,1,6,-3]]
print(number_of_terms(polynomial))