

full_projection_from_python := proc(polynomials_in_matricial_form::list(list(list(numeric))), variable_order::list(posint))
    description "This procedure takes a set of polynomials described in matricial form and returns the matricial form of all the polynomials generated on each step of the projection following the given variable order.":
    local polynomials_in_maple::list(polynom(numeric)), variable_order_in_maple::list(name), projected_polynomials_in_maple::list(list(polynom(numeric))), projected_polynomials_step::list(polynom(numeric)), projected_polynomials_in_matricial_form::list(list(list(numeric))):

    polynomials_in_maple := sparse_matrix_to_polynomial~(polynomials_in_matricial_form): # The original polynomials given in matricial form are written in a standard way using variables of the form x_i with i>=1. 
    variable_order_in_maple := [seq(x[i], i in variable_order)]: # The variable order is written in the appropiate variables.
    projected_polynomials_in_maple := McCallumProjectionSimple(polynomials_in_maple,variable_order_in_maple):-ListProjPolys(): # This procedure returns a list of lists of the projected polynomials on each step.
    projected_polynomials_in_matricial_form := [seq(polynomial_to_sparse_matrix~(projected_polynomials_step, indets(projected_polynomials_step)), projected_polynomials_step in projected_polynomials_in_maple)]: # These polynomials are written in matricial form.
    return projected_polynomials_in_matricial_form:
end proc:

projection_step_from_python := proc(polynomials_in_matricial_form::list(list(list(numeric))), variable_to_project::posint)
    description "This procedure takes a set of polynomials described in matricial form and returns their projection over the requested variable in matricial form":
    local polynomials_in_maple::list(polynom(numeric)), variable_to_project_in_maple::posint, auxiliary_variable::name, projected_polynomials_in_maple::list(polynom(numeric)), projected_polynomials_in_matricial_form::list(list(list(numeric))), variables::list(name), new_variables::list(name):

    polynomials_in_maple := sparse_matrix_to_polynomial~(polynomials_in_matricial_form): # The original polynomials given in matricial form are written in a standard way using variables of the form x_i with i>=1.
    variable_to_project_in_maple := convert("x_"||variable_to_project, name): # The variable to project is written in the appropiate way.
    variables := indets(polynomials_in_maple):
    new_variables := variables minus {variable_to_project_in_maple}: # The new polynomials will use ony these variables
    if numelems(new_variables)=0 then 
        # return []:
        error("It is not possible to project a univariate polynomial."): 
    end if:
    auxiliary_variable := new_variables[1]: # Another variable is needed to make the projection using 'McCallumProjectionSimple'
    projected_polynomials_in_maple := McCallumProjectionSimple(polynomials_in_maple,[auxiliary_variable, variable_to_project_in_maple]):-ListProjPolys()[1]: # McCallumProjectionSimple require two varibles to project over the second one, if only one is sent no projection is done. Also this procedure returns a list, the first element of that list is a list containing the projected polynomials of our interest.
    projected_polynomials_in_matricial_form := polynomial_to_sparse_matrix~(projected_polynomials_in_maple, [seq(new_variables, poly in projected_polynomials_in_maple)]): # These polynomials are written in matricial form.
    return projected_polynomials_in_matricial_form:
end proc:

CAD_from_python := proc(polynomials_in_matricial_form::list(list(list(numeric))), variable_order::list(posint))
    description "This procedure takes a set of polynomials described in matricial form and a variable order and returns the projected polynomials on each step on the projection in a vector of their matricial forms.":

    local rational_polynomials_in_matricial_form, polynomials_in_maple, variable_order_in_maple, R, cad, ncells:

    #rational_polynomials_in_matricial_form := force_rational_coeffs~(polynomials_in_matricial_form): # This change the coefficients to rationals for the polynomials to be accepted by CylindricalAlgebraicDecompose()
    print("notratcoeffs: ", polynomials_in_matricial_form):
    polynomials_in_maple := sparse_matrix_to_polynomial~(polynomials_in_matricial_form): # The original polynomials given in matricial form are written in a standard way using variables of the form x_i with i>=1.
    print("ratpolys: ", polynomials_in_maple):
    variable_order_in_maple := [seq(x_||i, i in variable_order)]: # The variable order is written in the appropiate variables.
    R := PolynomialRing(variable_order_in_maple):
    cad := CylindricalAlgebraicDecompose(polynomials_in_maple, R, output=cadcell):
    ncells := nops(cad):    

    return ["No function that returns the projected polynomials",ncells]: #when amir has a function to see the proj polynomials they will be returned here
end proc: