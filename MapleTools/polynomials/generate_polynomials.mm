create_multivariates_from_python := proc(used_variables, nterms, exponents, coefficients)
    description 
    "This procedure returns a polynomial for each entry of the given lists, such polynomials: -Use the variables described in the entry 'used_variables'. -Use random exponents from the list 'exponents'. -Have the number of terms indicated in the entry of 'nterms'. -Use random coefficients from the list 'coefficients'.":
    local npolynomials, variables_fun, variables, rc, random_in_coefficients, re, random_in_exponents, get_random_polynomial, polynomials_in_normal_form, k, new_polynomial, polynomials_in_matricial_form, all_variables, rep:
    npolynomials := numelems(nterms): 
    variables_fun := [aux_list -> seq(x[i], i in SearchAll(1,aux_list))]: # has the hability to create a list of variables given an entrance of the used variables
    variables := [seq(variables_fun(vars), vars in used_variables)]: # creates a list of lists with the desired variables
    rc:=rand(1..numelems(coefficients)):
    random_in_coefficients := ()-> coefficients[rc()]: # returns a random element in coefficients
    
    re:=rand(1..numelems(exponents)):
    random_in_exponents := ()-> exponents[re()]: # returns a random element in coefficients

    get_random_polynomial := (vars, numterms) -> randpoly(vars,expons=random_in_exponents,terms=numterms, coeffs=random_in_coefficients):

    polynomials_in_normal_form := []:
    for k from 1 to npolynomials do
        new_polynomial := 0:
        rep := 0:
        while count_terms(new_polynomial)<>nterms[k] or indets(new_polynomial)<>convert(variables[k],set) do #makes sure that every polynomial has the appropiate number of terms and uses all the variables
            new_polynomial := get_random_polynomial(variables[k],nterms[k]+rep):
            if count_terms(new_polynomial)<nterms[k] then
                rep:=rep+1:
            elif count_terms(new_polynomial)>nterms[k] then
                rep:=rep-1:
            end if:
        end do:
        polynomials_in_normal_form := [op(polynomials_in_normal_form),new_polynomial]:
    end do:

    all_variables := indets(polynomials_in_normal_form):
    polynomials_in_matricial_form := [seq(polynomial_to_sparse_matrix(polynomial, all_variables), polynomial in polynomials_in_normal_form)]:
    return polynomials_in_matricial_form:
end proc:

create_random_multivariates_from_python := proc()
    description 
    "This procedure returns a list of 2 to 4 polynomials, such polynomials: -Use four variables. -Use random exponents generated using 'random_expons'. -Have at least 2 terms. -Use random coefficients between -3 and 3.":
    local npolynomials, variables_fun, variables, rc, random_in_coefficients, re, random_in_exponents, polynomials_in_normal_form, k, new_polynomial, polynomials_in_matricial_form, all_variables, nterms, random_expons:

    npolynomials := rand(2..4)():
    variables:= [seq(x[i], i = 1..4)]:
    rc:=rand(0..3):
    random_expons := ()-> min(rc(),rc()):
    polynomials_in_normal_form := []:
    for k from 1 to npolynomials do
        nterms := 4:
        new_polynomial := 0:
        while count_terms(new_polynomial)<2 or numelems(indets(new_polynomial))<2 do #makes sure that every polynomial has an appropiate number of terms and uses all the variables
            new_polynomial := randpoly(variables, expons=random_expons, terms=nterms, coeffs=rand((-3)..3)):
            #new_polynomial := remove_terms_high_degree(new_polynomial, 4):
            nterms := nterms + 1:
        end do:
        polynomials_in_normal_form := [op(polynomials_in_normal_form),new_polynomial]:
    end do:

    all_variables := indets(polynomials_in_normal_form):
    polynomials_in_matricial_form := [seq(polynomial_to_sparse_matrix(polynomial, all_variables), polynomial in polynomials_in_normal_form)]:
    return polynomials_in_matricial_form:
end proc:

remove_terms_high_degree:=proc(f::polynom(numeric),n::posint)
    description "This function can remove the terms of degree higher than 'n' in the polynomial 'f'":
    local terms, small_degree:
    terms := return_terms(f):
    small_degree:=(t,m) -> if degree(t)<=m and numelems(indets(t))>=2 then t else 0 end if:
    add(seq(small_degree(term,n), term in terms)):
end proc:
