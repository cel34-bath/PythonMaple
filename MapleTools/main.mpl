
if kernelopts(platform) = "unix" then
    initial_directory := FileTools:-JoinPath( ["/home", "delriot", "Documents", "Repositories"], platform = kernelopts(platform)):
else:
    initial_directory := FileTools:-JoinPath( ["C:", "Users", "teres", "OneDrive - Coventry University", "Repositories"], platform = kernelopts(platform) ):
end if:

libname,=currentdir():
print(currentdir()):
with(DEWCAD):
with(SMTLIB):
with(RootFinding):
with(StringTools):
with(ListTools):
with(ArrayTools):
with(RegularChains):
with(SemiAlgebraicSetTools):


unprotect('TeresoTools'):

TeresoTools := module()
    option package:
    description "This package contains a set of useful tools for Tereso.":

    local estandarise_polynomials, 
    full_projection_from_python, 
    individual_number_of_roots_from_python, 
    recurrent_polynomial_list, 
    remove_terms_high_degree, 
    count_terms, return_terms, 
    polynomial_to_vector_for_python:

    export polynomials_in_file_for_python, 
    sparse_matrix_to_polynomial, 
    projection_step_from_python, 
    create_multivariates_from_python, 
    create_random_multivariates_from_python, 
    number_of_roots_from_python, 
    polynomial_to_sparse_matrix,
    CAD_from_python, 
    force_rational_coeffs:

# including objects.
$include "CAD\\CAD_tools.mm"
$include "polynomials\\counting_roots.mm"
$include "polynomials\\extract_polynomials.mm"
$include "polynomials\\generate_polynomials.mm"
$include "polynomials\\polynomial_tools.mm"

    # end of the package
end module:

protect('TeresoTools'):