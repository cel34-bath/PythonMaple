import os
import sys

cwd = os.getcwd()
if "Repositories" in cwd:
    initial_directory = cwd.split("Repositories")[0]+"Repositories"
else:
    raise Exception("You're too far from Repositories.")
    
import sys
sys.path.append('./')
from WorkWithMaple.UseMaple.use_maple_from_python import create_run_maple_from_python


def generate_multivariate_mimicking_by_maple(used_variables,nterms, exponents, coefficients):
    '''This function will receive an instance of polynomials in a real example and will generate new random ones using maple'''

    auxiliar_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_file_mimicking.mpl")
    output_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_output.txt")
    aux = create_run_maple_from_python(file_location=auxiliar_file, libnames_needed=[os.path.join(initial_directory, "02Tools", "MapleTools")], packages_needed=["TeresoTools"], initializations=[("used_variables",used_variables),("exponents",exponents),("nterms",nterms),("coefficients",coefficients)], functions_to_call=[("create_multivariates_from_python", ["used_variables","nterms","exponents","coefficients"], "polynomials_python")] ,output_files=[(output_file,"polynomials_python")])
    polynomials = aux[1] # create_run_maple_from_python returns a vector containing the time in position 0 and the desired outputs after
    return polynomials

def generate_multivariate_random_by_maple():
    '''This function will receive an instance of polynomials in a real example and will generate new random ones using maple'''

    auxiliar_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_file_mimicking.mpl")
    output_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_output.txt")
    aux = create_run_maple_from_python(file_location=auxiliar_file, libnames_needed=[os.path.join(initial_directory, "02Tools", "MapleTools")], packages_needed=["TeresoTools"],  initializations=[], functions_to_call=[("create_random_multivariates_from_python", [], "polynomials_python")] ,output_files=[(output_file,"polynomials_python")])
    polynomials = aux[1] # create_run_maple_from_python returns a vector containing the time in position 0 and the desired outputs after

    return polynomials

def generate_similar_problem(original:list=[], change_npoly:bool=False, change_nterms:bool=False, change_used_variables:bool=False, change_degrees:bool=False, change_coeffs:bool=False):
    pass


def generate_similar_multivariate(original:list=[], change_npoly:bool=False):
    pass