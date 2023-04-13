count_terms := proc(f::polynom)
    description "Returns the number of terms in a polynomial":
    local fe := expand(f): if fe=0 then 0 elif type(fe, `+`) then nops(fe) else 1 end if: 
end proc: 

return_terms := proc(f::polynom)
    description "Returns the terms in a polynomial":
    local fe := expand(f): if fe=0 then [] elif type(fe, `+`) then [op(fe)] else [fe] end if:
end proc: 

polynomial_to_sparse_matrix := proc(polynomial::polynom, variables::Or(list(name), set(name)) := convert(indets(polynomial),list))
    description "This procedure converts a polynomial into a sparse matricial form. 3x^2y^3 + 2xz - 7xy^2z^3 is expressed as [[2,3,0,3],[1,0,1,2],[1,2,3,-7]]. Each of the vectors of the vector describes a monomial. The last element is the coefficient and the others the exponents of the variables.":
    local sparse_matricial_form, i, term, coef, position, var, descriptor:

    sparse_matricial_form := []:
    if type(polynomial,`+`) then
        for term in polynomial do # the elements of polynomial are the monomials
            coef := coeffs(term): #e.g. -96
            descriptor := [seq(degree(term, var), var in variables), coef]: #e.g. [2,0,3,-96] -96*x^2*z^3 if variables:=[x,y,z]
            sparse_matricial_form := [op(sparse_matricial_form), descriptor]:
        end do:
    else:
        coef := coeffs(polynomial): #e.g. -96
        descriptor := [seq(degree(polynomial, var), var in variables), coef]: #e.g. [2,0,3,-96] -96*x^2*z^3 if variables:=[x,y,z]
        sparse_matricial_form := [op(sparse_matricial_form), descriptor]:
    end if:
    return sparse_matricial_form:
end proc:

sparse_matrix_to_polynomial := proc(sparse_matricial_form::list(list(numeric)))
    description "This procedure converts a polynomial expressed as an sparse matrix into its normal form. [[2,3,0,3],[1,0,1,2],[1,2,3,-7]] represents 3x_1^2x_2^3 + 2x_1x_3 - 7x_1x_2^2x_3^3. Each of the vectors (descriptors) of the vector (matricial form) describes a monomial. The last element is the coefficient and the others the exponents of the variables.":
    local polynomial, descriptor, monomial_terms:

    polynomial := 0:
    for descriptor in sparse_matricial_form do
        monomial_terms := [seq(convert("x_"||i,name)^descriptor[i],i in 1..nops(descriptor)-1),convert(descriptor[-1], rational, exact)]: #exact can be added to have more digits
        polynomial := polynomial + `*`(monomial_terms[]):
    end do:

    return polynomial:
end proc:

# DOESNT WORK
estandarise_polynomials := proc(original_polynomials)
    description "Returns a list of the given polynomials where the name of the variables is standarised.":
    local k, changes, variable, new_final_list, poly, changes_poly, new_poly, new_new_final_list:

    k := 0:
    changes := "subs([":
    for variable in indets(final_list) do
        k := k + 1:
        changes := cat(changes, "`",variable, "`=", "x_", k, ","):
    end do:

    changes := cat(substring(changes,1..-2), "], original_polynomials):"):
    new_final_list := eval(parse(changes)):
    new_new_final_list := parse(convert(new_final_list, string), statement):

    return new_new_final_list:
end proc:

force_rational_coeffs := proc(polynomial_in_matricial_form::list(list(numeric)))
    description "Makes sure that all the coefficients in a polynomial are rational":
    local rational_polynomial_in_matricial_form, monom, rational_monomial:

    rational_polynomial_in_matricial_form := []:
    for monom in polynomial_in_matricial_form do
        rational_monomial := [op(monom[1..-2]), convert(monom[-1],rational, exact)]:#exact can be added to have more digits
        rational_polynomial_in_matricial_form := [op(rational_polynomial_in_matricial_form), rational_monomial]:
    end do:
end proc:
