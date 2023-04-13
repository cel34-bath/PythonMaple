import os
import sys
import random 
import pickle

cwd = os.getcwd()
if "Repositories" in cwd:
    initial_directory = cwd.split("Repositories")[0]+"Repositories"
else:
    raise Exception("You're too far from Repositories.")

from .polynomial_characteristics import number_of_terms


default_max_nvar = 6

class Polynomial:
    def __init__(self, matricial_form:list, subdir: str = None, file: str = None) -> None:
        if matricial_form!=[] and any(len(monomial)!=len(matricial_form[0]) for monomial in matricial_form):
            print(matricial_form, file)
            raise TypeError("A polynomial is described by a list of lists of the same lenght.")
        self.matricial_form = matricial_form
        self.subdir = subdir
        self.file = file
        self.nterms = number_of_terms(matricial_form)
        self.nvariables = len(matricial_form[0])-1 if matricial_form!=[] else 0
        self.used_variables = [int(sum(elem)!=0) for elem in zip(*[monomial[:-1] for monomial in self.matricial_form ])]
        self.max_degree = max([sum(monomial[:-1]) for monomial in self.matricial_form]) if matricial_form!=[] else 0

    def __str__(self):
        return f"{self.matricial_form}"

    def __repr__(self):
        return f"{self.matricial_form}"

    def is_univariate(self):
        return True if sum(self.used_variables)==1 else False

    def get_coeffs(self):
        return [monomial[-1] for monomial in self.matricial_form]

    def get_degrees(self):
        return [degree for monomial in self.matricial_form for degree in monomial[:-1] if degree != 0]

    def get_nterms(self):
        return self.nterms

    def get_used_variables(self):
        '''Returns a binary list indicating the variables used in this polynomial'''
        return self.used_variables

    def change_coeffs(self, possible_coeffs):
        new_polynomial = Polynomial([])
        i = 0
        while new_polynomial.nterms != self.nterms or new_polynomial.used_variables!=self.used_variables:
            if i>10:
                return new_polynomial
            i += 1
            new_polynomial = Polynomial([term[:-1]+[random.choice(possible_coeffs)] for term in self.matricial_form])
        return new_polynomial

    def change_degrees(self, possible_degrees):
        new_polynomial = Polynomial([])
        i = 0
        while new_polynomial.nterms != self.nterms or new_polynomial.used_variables!=self.used_variables:
            if i>10:
                return new_polynomial
            i += 1
            new_matricial_form = [[random.choice(possible_degrees) if var==1 else 0 for var in self.used_variables]+[term[-1]] for term in self.matricial_form]
            new_polynomial = Polynomial(new_matricial_form)
        return new_polynomial

    def change_degrees_and_coeffs(self, possible_coeffs, possible_degrees):
        new_polynomial = Polynomial([])
        i = 0
        while new_polynomial.nterms != self.nterms or new_polynomial.used_variables!=self.used_variables:
            if i>10:
                return new_polynomial
            i += 1
            new_matricial_form = [[random.choice(possible_degrees) if var==1 else 0 for var in self.used_variables]+[random.choice(possible_coeffs)] for _term in self.matricial_form]
            new_polynomial = Polynomial(new_matricial_form)
        return new_polynomial

    def change_nterms(self, possible_coeffs, possible_degrees, possible_nterms):
        new_polynomial = Polynomial([])
        i = 0
        while new_polynomial.used_variables!=self.used_variables:
            if i>10:
                return new_polynomial
            i += 1
            nterms = random.choice(possible_nterms)
            new_matricial_form = [[random.choice(possible_degrees) if var==1 else 0 for var in self.used_variables]+[random.choice(possible_coeffs)] for _term in range(nterms)]
            new_polynomial = Polynomial(new_matricial_form)
        return new_polynomial

    def change_used_variables(self, possible_coeffs, possible_degrees, possible_nterms, used_variables):
        nterms = random.choice(possible_nterms)
        new_polynomial = Polynomial([])
        i = 0
        while new_polynomial.used_variables!=used_variables:
            if i>10:
                return new_polynomial
            i += 1
            new_matricial_form = [[random.choice(possible_degrees) if var==1 else 0 for var in used_variables]+[random.choice(possible_coeffs)] for _term in range(nterms)]
            new_polynomial = Polynomial(new_matricial_form)
        return new_polynomial

    def keep_only_this_vars(self, chosen_vars):
        new_matricial_form = [ [term[i] for i in chosen_vars+[-1]]  for term in self.matricial_form]
        new_polynomial = Polynomial(new_matricial_form)
        return new_polynomial

 

class Problem:
    def __init__(self, polynomials:list, subdir: str = None, file: str = None, max_nvar: str = default_max_nvar) -> None:
        if polynomials!=[] and any(poly.nvariables!=polynomials[0].nvariables for poly in polynomials):
            raise TypeError("A Problem is described by a list of Polynomial with the same number of variables.")
        self.nvariables = polynomials[0].nvariables if polynomials !=[] else 0
        if self.nvariables <= max_nvar:
            self.polynomials = polynomials
        else:
            self.polynomials = []
        self.npolynomials = len(polynomials)
        self.subdir = subdir
        self.file = file

    def __str__(self):
        return ",".join([f"{polynomial}" for polynomial in self.polynomials])

    def __repr__(self):
        return ",".join([f"{polynomial}" for polynomial in self.polynomials])

    def get_matricial_forms(self):
        return [poly.matricial_form for poly in self.polynomials]

    def get_coeffs(self):
        return [coeff for poly in self.polynomials for coeff in poly.get_coeffs()]

    def get_degrees(self):
        return [degree for poly in self.polynomials for degree in poly.get_degrees()]

    def get_nterms(self):
        return [poly.get_nterms() for poly in self.polynomials]

    def get_used_variables(self):
        '''Returns a list of binary lists indicating the variables used on each polynomials of the problem'''
        return [poly.get_used_variables() for poly in self.polynomials]

    def create_similar_polynomial_set(self, procedure, possible_coeffs, possible_degrees, possible_nterms, possible_used_variables, max_nvar:int=3):

        if self.nvariables > max_nvar:
            chosen_vars = random.sample(range(self.nvariables),max_nvar) # the rest of the variables will be removed
            original_polynomials = [poly.keep_only_this_vars(chosen_vars) for poly in self.polynomials]
        else:
            original_polynomials = self.polynomials
        print("procedure", procedure)
        if procedure == 0:
            new_polynomials =  self
        elif procedure == 1:
            new_polynomials =  [poly.change_coeffs(possible_coeffs) for poly in original_polynomials]
        elif procedure == 2:
            new_polynomials =  [poly.change_degrees(possible_degrees) for poly in original_polynomials]
        elif procedure == 3:
            new_polynomials =  [poly.change_degrees_and_coeffs(possible_coeffs, possible_degrees) for poly in original_polynomials]
        elif procedure == 4:
            new_polynomials =  [poly.change_nterms(possible_coeffs, possible_degrees, possible_nterms) for poly in original_polynomials]
        elif procedure == 5:
            list_used_variables = [random.choice(possible_used_variables) for _ in original_polynomials]
            nvar = max([len(used_vars) for used_vars in list_used_variables]) if list_used_variables != [] else 0
            for used_vars in list_used_variables:
                while len(used_vars)<nvar:
                    used_vars.insert(random.randint(0, len(used_vars)), 0)
            new_polynomials =  [poly.change_used_variables(possible_coeffs, possible_degrees, possible_nterms, used_variables) for poly, used_variables in zip(original_polynomials, list_used_variables)]
        return new_polynomials

    def create_similar_problem(self, procedure, possible_coeffs, possible_degrees, possible_nterms, possible_used_variables, max_nvar:int=3):
        polynomials = self.create_similar_polynomial_set(procedure, possible_coeffs, possible_degrees, possible_nterms, possible_used_variables)
        return Problem(polynomials, self.subdir+"_synthetic_"+str(procedure), self.file+"_synthetic_"+str(procedure))


class Folder:
    def __init__(self, problems:list, subdir: str = None, file: str = None) -> None:
        self.problems = problems
        self.nproblems = len(problems)
        self.subdir = subdir
        self.file = file

    def __str__(self):
        return ",".join([f"{problem}" for problem in self.problems])

    def __repr__(self):
        return ",".join([f"{problem}" for problem in self.problems])

    def get_coeffs(self):
        return [coeff for problem in self.problems for coeff in problem.get_coeffs()]

    def get_degrees(self):
        return [degree for problem in self.problems for degree in problem.get_degrees()]

    def get_nterms(self):
        return [nterms for problem in self.problems for nterms in problem.get_nterms()]

    def get_used_variables(self):
        return [used_variables for problem in self.problems for used_variables in problem.get_used_variables()]

    def get_deep_problems(self):
        problems = []
        for elem in self.problems:
            if type(elem) == Problem:
                problems += [elem]
            elif type(elem) == Folder:
                problems += elem.get_deep_problems()
        return problems

    def info_for_synthetic_data(self):
        possible_coeffs = self.get_coeffs()
        possible_degrees = self.get_degrees()
        possible_nterms = self.get_nterms()
        possible_used_variables = self.get_used_variables()
        possible_problems = [problem for problem in self.problems if problem.polynomials != []]
        return possible_coeffs, possible_degrees, possible_nterms, possible_problems, possible_used_variables

   



    def create_synthetic_data(self, procedure:int=0, size:int=10):
        possible_coeffs, possible_degrees, possible_nterms, possible_problems, possible_used_variables = self.info_for_synthetic_data()
        new_problems = []
        print("Possible problems "+self.subdir+" are "+ str(len(possible_problems)))
        print(possible_problems)
        i = 0
        for _ in range(size):
            chosen_problem = random.choice(possible_problems)
            i+=1
            print(i)
            #chosen_problem = random.choice(possible_problems)
            new_problems.append(chosen_problem.create_similar_problem(procedure, possible_coeffs, possible_degrees, possible_nterms, possible_used_variables))
        print(new_problems)
        return Folder(new_problems, self.subdir+"_synthetic_"+str(procedure), self.file+"_synthetic_"+str(procedure))

    def save(self, *args):
        f = open(os.path.join(initial_directory, "Data", "ZerosPolynomials", "All", *args), "wb")
        pickle.dump(self, f)

