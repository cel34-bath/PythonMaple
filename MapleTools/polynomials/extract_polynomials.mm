recurrent_polynomial_list := proc(expression::Or(function,`<`,`<=`,`<>`,`=`))
    description "This procedure calls itself recurrently to find all the polynomials in a nested logical expression of constraints":
    local new_expression, new_polynomial::polynom(numeric), polynomial_list::list(polynom(numeric)):

    polynomial_list := []:

    if type(expression, Or(`<`,`<=`,`<>`,`=`)) then
        new_polynomial := op(1,expression)-op(2,expression):
        polynomial_list := [op(polynomial_list), new_polynomial]:
    elif type(expression, function) then
        for new_expression in expression do
            polynomial_list := [op(polynomial_list), op(recurrent_polynomial_list(expand(new_expression)))]:
        end do:
    end if:

    return polynomial_list:
end proc:

polynomials_in_file_for_python := proc(file_name::string)
    description "This procedure returns a set of the polynomials from the problem described in file_name":
    local problem, polynomials,  variables, polynomial, polynomials_for_python, standarised_polynomials:
    
    problem := ParseFile(file_name):
    # the problem is described in problem
    
    polynomials := recurrent_polynomial_list(problem):
    standarised_polynomials := standarise_polynomials(polynomials):
    variables := indets(polynomials):
    polynomials_for_python := [seq(polynomial_to_sparse_matrix(polynomial, variables), polynomial in polynomials)]:
    return polynomials_for_python
end proc:

