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
    # print("output", maple_output)
    return maple_output[2]