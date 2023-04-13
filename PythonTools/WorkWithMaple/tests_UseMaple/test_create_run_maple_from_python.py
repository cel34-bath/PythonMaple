import os
import sys
sys.path.append('./')

id = "oyl"
timeout = 10
initial_directory = os.path.join("C:\\", "Users", "teres",
                                 "OneDrive - Coventry University",
                                 "03Repositories")
polynomials = [[[1, 0, 1]], [[0, 1, 1]], [[0, 0, -213], [0, 1, 655]]]
variable = 1
auxiliar_file = os.path.join(initial_directory, '03CADVariableOrdering',
                             "Auxiliar", "maple_from_python_file_proj"
                             + id + ".mpl")
output_file = os.path.join(initial_directory, '03CADVariableOrdering',
                           "Auxiliar", "maple_from_python_output"+id+".txt")


def test_create_run_maple_from_python():
    """This is a shitty test but it is best than anything."""
    from UseMaple.use_maple_from_python import create_run_maple_from_python
    aux = create_run_maple_from_python(
        file_location=auxiliar_file,
        libnames_needed=[os.path.join(initial_directory,
                                      "02Tools", "MapleTools")],
        packages_needed=["TeresoTools"],
        initializations=[("polynomials_python", polynomials)],
        functions_to_call=[("projection_step_from_python",
                           ["polynomials_python", str(variable)],
                           "proj_polys")],
        output_files=[(output_file, "proj_polys")], timelimit=timeout)

    assert aux[1] == [[[1, 1]], [[0, -213], [1, 655]]], ("The return"
           "polynomials aren't the projection")



def test_create_run_maple_from_python():
    """This is a shitty test but it is best than anything."""
    from UseMaple.use_maple_from_python import create_run_maple_from_python
    aux = create_run_maple_from_python(
        file_location=auxiliar_file,
        libnames_needed=[os.path.join(initial_directory,
                                      "02Tools", "MapleTools"),
                         os.path.join(initial_directory, "01DEWCADCoventry",
                                      "Packages", "SimpleCAD"),
                         os.path.join(initial_directory, "01DEWCADCoventry",
                                      "Packages", "RationalNumbers")],
        packages_needed=["TeresoTools", "SimpleCAD", "RationalNumbers"],
        initializations=[("polynomials_python", polynomials)],
        functions_to_call=[("projection_step_from_python",
                           ["polynomials_python", str(variable)],
                           "proj_polys")],
        output_files=[(output_file, "proj_polys")], timelimit=timeout)

    assert aux[1] == [[[1, 1]], [[0, -213], [1, 655]]], ("The return"
           "polynomials aren't the projection")
