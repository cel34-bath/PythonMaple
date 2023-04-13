import os
import sys
import random 
import pickle

cwd = os.getcwd()
if "Repositories" in cwd:
    initial_directory = cwd.split("Repositories")[0]+"Repositories"
else:
    raise Exception("You're too far from Repositories.")

from .polynomial_characteristics import number_of_roots_by_maple, number_of_terms
from .extract_univariates import recurrent_project_searching_univariates

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
        return [degree for monomial in self.matricial_form for degree in monomial[:-1]]

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
            new_polynomial = Polynomial([[random.choice(possible_degrees) if var==1 else 0 for var in self.used_variables]+[term[-1]] for term in self.matricial_form])
        return new_polynomial

    def change_degrees_and_coeffs(self, possible_coeffs, possible_degrees):
        new_polynomial = Polynomial([])
        i = 0
        while new_polynomial.nterms != self.nterms or new_polynomial.used_variables!=self.used_variables:
            if i>10:
                return new_polynomial
            i += 1
            new_polynomial = Polynomial([[random.choice(possible_degrees) if var==1 else 0 for var in self.used_variables]+[random.choice(possible_coeffs)] for _term in self.matricial_form])
        return new_polynomial

    def change_nterms(self, possible_coeffs, possible_degrees, possible_nterms):
        new_polynomial = Polynomial([])
        i = 0
        while new_polynomial.used_variables!=self.used_variables:
            if i>10:
                return new_polynomial
            i += 1
            nterms = random.choice(possible_nterms)
            new_polynomial = Polynomial([[random.choice(possible_degrees) if var==1 else 0 for var in self.used_variables]+[random.choice(possible_coeffs)] for _term in range(nterms)])
        return new_polynomial

    def change_used_variables(self, possible_coeffs, possible_degrees, possible_nterms, used_variables):
        nterms = random.choice(possible_nterms)
        new_polynomial = Polynomial([])
        i = 0
        while new_polynomial.used_variables!=used_variables:
            if i>10:
                return new_polynomial
            i += 1
            new_polynomial = Polynomial([[random.choice(possible_degrees) if var==1 else 0 for var in used_variables]+[random.choice(possible_coeffs)] for _term in range(nterms)])
        return new_polynomial

    def keep_only_this_vars(self, chosen_vars):
        new_matricial_form = [ [term[i] for i in chosen_vars+[-1]]  for term in self.matricial_form]
        new_polynomial = Polynomial(new_matricial_form)
        return new_polynomial


max_nvar = 6


class Problem:
    def __init__(self, polynomials:list, subdir: str = None, file: str = None) -> None:
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
        self.univariates_with_nroots = self.get_univariates_with_nroots()
        self.univar_nroots = self.univariates_nroots()

    def __str__(self):
        return ",".join([f"{polynomial}" for polynomial in self.polynomials])

    def __repr__(self):
        return ",".join([f"{polynomial}" for polynomial in self.polynomials])

    def get_matricial_forms(self):
        return [poly.matricial_form for poly in self.polynomials]

    def univariates_nroots(self, max_degree:int=10):
        '''This returns the number of roots of the univariates polynomials in the problem of degree smaller or equal than 'max_degree' '''
        return [[univariate.max_degree, univariate.nroots] for univariate in self.get_univariates_with_nroots()]

    def get_univariates_with_nroots(self, max_degree:int=10):
        '''This returns a list of univariates extracted from the problem of degree smaller or equal than 'maxdegree' with the attribute 'nroots' '''
        try:
            return self.univariates_with_nroots
        except AttributeError:
            univariates_without_nroots = [Polynomial(univariate) for univariate in recurrent_project_searching_univariates(self.get_matricial_forms(), max_nvar=max_nvar)]
            univariates_with_nroots = []
            for degree in range(2, max_degree+1):
                interesting_univariates = [univariate for univariate in univariates_without_nroots if univariate.max_degree == degree] #univariates of the desired degree
                nroots_list = number_of_roots_by_maple([univariate.matricial_form for univariate in interesting_univariates]) # The number of roots is computed
                for univariate, nroots in zip(interesting_univariates, nroots_list): 
                    univariate.nroots = nroots # They are added as an attribute for their corresponding univariate
                    univariates_with_nroots.append(univariate)
            self.univariates_with_nroots = univariates_with_nroots
            return self.univariates_with_nroots

    def get_coeffs(self):
        return [coeff for poly in self.polynomials for coeff in poly.get_coeffs()]

    def get_degrees(self):
        return [degree for poly in self.polynomials for degree in poly.get_degrees()]

    def get_nterms(self):
        return [poly.get_nterms() for poly in self.polynomials]

    def get_used_variables(self):
        '''Returns a list of binary lists indicating the variables used on each polynomials of the problem'''
        return [poly.get_used_variables() for poly in self.polynomials]

    def create_similar_problem(self, procedure, possible_coeffs, possible_degrees, possible_nterms, possible_used_variables, max_nvar:int=3):

        if self.nvariables > max_nvar:
            chosen_vars = random.sample(range(self.nvariables),max_nvar) # the rest of the variables will be removed
            original_polynomials = [poly.keep_only_this_vars(chosen_vars) for poly in self.polynomials]
        else:
            original_polynomials = self.polynomials
        print("procedure", procedure)
        if procedure == 0:
            polynomials =  self
        elif procedure == 1:
            polynomials =  [poly.change_coeffs(possible_coeffs) for poly in original_polynomials]
        elif procedure == 2:
            polynomials =  [poly.change_degrees(possible_degrees) for poly in original_polynomials]
        elif procedure == 3:
            polynomials =  [poly.change_degrees_and_coeffs(possible_coeffs, possible_degrees) for poly in original_polynomials]
        elif procedure == 4:
            polynomials =  [poly.change_nterms(possible_coeffs, possible_degrees, possible_nterms) for poly in original_polynomials]
        elif procedure == 5:
            list_used_variables = [random.choice(possible_used_variables) for _ in original_polynomials]
            nvar = max([len(used_vars) for used_vars in list_used_variables]) if list_used_variables != [] else 0
            for used_vars in list_used_variables:
                while len(used_vars)<nvar:
                    used_vars.insert(random.randint(0, len(used_vars)), 0)
            polynomials =  [poly.change_used_variables(possible_coeffs, possible_degrees, possible_nterms, used_variables) for poly, used_variables in zip(original_polynomials, list_used_variables)]
        return Problem(polynomials, self.subdir+"_synthetic_"+str(procedure), self.file+"_synthetic_"+str(procedure))


class Folder:
    def __init__(self, problems:list, subdir: str = None, file: str = None) -> None:
        self.problems = problems
        self.nproblems = len(problems)
        self.subdir = subdir
        self.file = file
        self.univar_nroots = self.univariates_nroots()

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

    def univariates_nroots(self):
        '''This returns the number of roots of the univariates polynomials in the folder computing only the ones that weren't computed already'''
        return [nroots for problem in self.problems for nroots in problem.univar_nroots] # problem could stand for problem or for a folder

    def create_synthetic_data(self, procedure:int=0, size:int=10):
        new_problems = []
        possible_coeffs = self.get_coeffs()
        possible_degrees = self.get_degrees()
        possible_nterms = self.get_nterms()
        possible_used_variables = self.get_used_variables()
        possible_problems = [problem for problem in self.problems if problem.polynomials != []]
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

