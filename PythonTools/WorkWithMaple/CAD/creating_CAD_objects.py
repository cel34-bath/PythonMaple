import os 
# import detect
import sys
import pickle

# if detect.linux:
initial_directory = os.path.join( "/home", "delriot", "Documents", "Repositories")
# elif detect.windows:
#     initial_directory = os.path.join( "C:\\", "Users", "teres", "OneDrive - Coventry University", "Repositories")

sys.path.append("./")
from WorkWithMaple.polynomials.polynomial_objects import Polynomial
from WorkWithMaple.polynomials.extract_univariates import get_polynomials_from_file
from WorkWithMaple.CAD.CAD_objects import CADProblem, CADFolder


def problems_in_directory_recurrent(working_directory, min_nvar:int = 3, max_nvar:int = 3):
    '''This function creates a dictionary describing a dataset that contains 
    all the real world polynomials in the directory and some of their characteristics'''

    problems_list = [] # problems or folders
    for subdir, dirs, files in os.walk(working_directory):
        print("SUBDIR", subdir)
        for file in files:
            print(file)
            polynomials = get_polynomials_from_file(os.path.join(subdir, file))
            # print("polys", polynomials)
            polynomials = [Polynomial(matricial_form, subdir, file) for matricial_form in polynomials]
            problem = CADProblem(polynomials, subdir, file)
            if min_nvar<=problem.nvariables and problem.nvariables<=max_nvar:
                problems_list.append(problem)
        for folder in dirs:
            problems_in_folder = problems_in_directory_recurrent(os.path.join(subdir, folder))
            problems_list.append(CADFolder(problems_in_folder, subdir, folder))
        return problems_list




