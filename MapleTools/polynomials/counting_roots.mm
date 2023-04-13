number_of_roots_from_python := proc(polynomials_in_matricial_form)
    description "This procedure takes a list of univariate polynomials described in their matricial form and returns a list of the number of roots each of those polynomials have":
    local polynomials_in_maple::list(polynom(numeric)), nroots::list(nonnegint), polynomial::polynom(numeric):

    polynomials_in_maple := sparse_matrix_to_polynomial~(polynomials_in_matricial_form): # The polynomials are translated to maple form
    nroots := [seq(numelems(Isolate(polynomial)), polynomial in polynomials_in_maple)]: # The number of roots is computed
    #nroots := [seq(add(seq(root_d[2], root_d in roots(polynomial))), polynomial in polynomials_in_maple)]:

    return nroots:
end proc:

individual_number_of_roots_from_python := proc(polynomial_in_matricial_form)
    description "This procedure takes a univariate polynomial described in their matricial form and returns a list of the number of roots that polynomials has":
    local polynomial_in_maple::polynom(numeric):

    polynomial_in_maple := sparse_matrix_to_polynomial(polynomial_in_matricial_form): # The polynomial is translated to maple form
    #nroots := [seq(numelems(Isolate(polynomial)), polynomial in polynomials_in_maple)]:
    return add(seq(root_d[2], root_d in roots(polynomial_in_maple))):
end proc: