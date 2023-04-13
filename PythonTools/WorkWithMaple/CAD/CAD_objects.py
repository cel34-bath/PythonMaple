"""This module contains the main objects used to describe and organize CADs."""
import itertools
import math
from functools import reduce
import operator
import random
import pickle
from numpy import Inf
from .CAD_tools import CAD_by_maple, first_vector_is_smaller_or_equal
from .CAD_tools import recurrent_project, remove_repeated
default_max_nvar = 4


class OneCAD:
    def __init__(
            self, polynomials: list,
            variable_order: list,
            timelimit: int = 30,
            projection=None,
            degrees_for_heuristics=None,
            proj_timing=None
            ):
        self.polynomials = polynomials
        self.variable_order = variable_order
        timing, projected_polynomials, ncells \
            = CAD_by_maple(polynomials, variable_order, timeout=timelimit)
        if timing == "Time over":
            # if the computation timed out
            self.timing = "Over " + str(timelimit)
        else:
            # if the computation finished
            self.timing = timing
        self.projected_polynomials = projected_polynomials 
        # save the polynomials early so that they can be recovered
        self.ncells = ncells

        # while we don't have a function that returns both the CAD 
        # and the proj polynomials we recur to
        if projection != None:
            self.projected_polynomials = projection
            self.degrees_for_heuristics = degrees_for_heuristics
            self.proj_timing = proj_timing

    def sotd(self):
        return sum([sum(monomial[:-1]) for level in self.projected_polynomials for polynomial in level for monomial in polynomial])

    def sotd_in_levels(self):
        return [sum(monomial[:-1]) for level in self.projected_polynomials for polynomial in level for monomial in polynomial]

    def mods(self):
        '''Multiplication of relative degrees. This gives an idea of the maximum number of root isolations that will be done if the projection with the chosen order gives this relative degrees.'''
        rough_max_number_of_root_isolations = reduce(operator.mul, self.degrees_for_heuristics, 1)
        return rough_max_number_of_root_isolations

    def logmods(self):
        '''Multiplication of the logarithm of relative degrees. This gives an idea of the expected number of root isolations that will be done if the projection with the chosen order gives this relative degrees.'''
        log_degrees = [(math.log(degree)+1) if degree != 0 else 1 for degree in self.degrees_for_heuristics]
        rough_approx_number_of_root_isolations = reduce(operator.mul, log_degrees, 1)
        return rough_approx_number_of_root_isolations

    def acc_mods(self):
        '''Multiplication of relative degrees. This gives the maximum number of root isolations that will be done if the projection with the chosen order gives this relative degrees.'''
        max_number_of_root_isolations_in_each_level = [reduce(operator.mul, [(2*degree+1) for degree in self.degrees_for_heuristics[:i]], self.degrees_for_heuristics[i]) for i in range(len(self.degrees_for_heuristics))]
        max_number_of_root_isolations = sum(max_number_of_root_isolations_in_each_level)
        return max_number_of_root_isolations

    def acc_logmods(self):
        '''Multiplication of relative degrees. This gives an accurate approximation (taking the log of the degree as a good approximation of the number of roots) of the number of root isolations that will be done if the projection with the chosen order gives this relative degrees.'''
        log_degrees = [(math.log(degree)+1) if degree != 0 else 1 for degree in self.degrees_for_heuristics]
        approx_number_of_root_isolations_in_each_level = [reduce(operator.mul, [(2*degree+1) for degree in log_degrees[:i]], log_degrees[i]) for i in range(len(log_degrees))]
        approx_number_of_root_isolations = sum(approx_number_of_root_isolations_in_each_level)
        return approx_number_of_root_isolations

class CADProblem():
    def __init__(self, polynomials: list = None, subdir: str = None, file: str = None, max_nvar: str = default_max_nvar, with_projections:bool=True):
        self.subdir = subdir
        self.file = file
        if polynomials!=[] and any(poly.nvariables!=polynomials[0].nvariables for poly in polynomials):
            raise TypeError("A Problem is described by a list of Polynomial with the same number of variables.")
        self.nvariables = polynomials[0].nvariables if polynomials !=[] else 0
        if self.nvariables <= max_nvar:
            self.polynomials = polynomials
        else:
            self.polynomials = []
        self.npolynomials = len(polynomials)
        self.nvariables = polynomials[0].nvariables if polynomials!=[] else 0
        if self.nvariables == 3:
            self.create_possible_CADs(with_projections=with_projections)

    def __str__(self):
        return "CADFolder:"+",".join([f"{polynomial}" for polynomial in self.polynomials])+";"

    def __repr__(self):
        return "CADFolder:"+",".join([f"{polynomial}" for polynomial in self.polynomials])+";"

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

    def create_possible_CADs(self, with_projections = True, timelimit = 30, strong_timelimit = 100):
        if with_projections is True:
            # Contrary to computing the CADs we do this only once for all orderings because some computations can be recycled
            projections, degrees_for_heuristics, proj_timings = recurrent_project([polynomial.matricial_form for polynomial in self.polynomials], return_for_heuristics = True)
        else:
            projections, degrees_for_heuristics, proj_timings = None, None, None

        self.timings = ["over 0"]*math.factorial(self.nvariables)
        #while all([type(timing)==str for timing in self.timings]) and timelimit<strong_timelimit:
        print("Lets see if this problem can be solved with ", timelimit)
        # while none of the possible orderings finished in the given time
        possible_CADs = []
        for oneCAD_projection, oneCAD_degrees_for_heuristics, variable_order, proj_timing in zip(projections, degrees_for_heuristics, itertools.permutations(range(1, self.nvariables+1), self.nvariables), proj_timings):
            possible_CADs.append(OneCAD(self.polynomials, list(variable_order), timelimit=timelimit, projection=oneCAD_projection, degrees_for_heuristics=oneCAD_degrees_for_heuristics, proj_timing=proj_timing))
        self.possible_CADs = possible_CADs
        self.timings = [cad.timing for cad in self.get_possible_CADs()]
        print("TIMINGS:", self.timings)

        
    
    def get_possible_CADs(self, force=False, with_projections= True):
        try:
            if force is False:
                # We don't force the computation of the CADs if we already have them
                return self.possible_CADs
            else:
                # To force the computation of the CADs we create an AttributeError
                self._non_existing_attribute
        except AttributeError:
            self.create_possible_CADs(with_projections=with_projections)
        return self.possible_CADs
    
    def get_timings(self):
        '''
        Returns the timings of its possible CADs.
        0.11 is removed from the timings because it's the estimated time to call Maple.
        '''
        return [cad.timing-0.075 if type(cad.timing)!=str else cad.timing for cad in self.get_possible_CADs()]

    def get_times_invested_in_projection(self):
        '''
        Returns the time invested in computing all the projections minus the time of the projections of the chosen order.
        '''
        unique_all_timings = set()
        for possible_CAD in self.get_possible_CADs():
            if hasattr(possible_CAD, "proj_timing"):
                unique_all_timings = unique_all_timings.union(possible_CAD.proj_timing[:-1]) # the last timing is always 0 as there is no need to project only one variable
        if len(unique_all_timings)>9: 
            print(unique_all_timings)
            raise Exception ("This is too many timings, there must be a problem. Disclaimer: this exception is only for 3 variables")
        reasonable_timings = [10 if timing==999999 else timing for timing in unique_all_timings] # when there is a problem the timing is set to 999999, but we wanna be reasonable here. In particular we will delete this timings because I don't know what is reasonable to include here
        timing_minus_maple_call = [max(0,timing-0.075) if type(timing)!=str else timing for timing in reasonable_timings] # calling maple takes up to 0.075 seconds
        total_timing = sum(timing_minus_maple_call)
        timings_minus_chosen = []
        for chosen_CAD in self.get_possible_CADs():
            if hasattr(chosen_CAD, "proj_timing"):
                reasonable_timings_order = [10 if timing==999999 else timing for timing in chosen_CAD.proj_timing] # when there is a problem the timing is set to 999999, but we wanna be reasonable here. In particular we will delete this timings because I don't know what is reasonable to include here
                timing_order_minus_maple_call = sum([max(0,timing-0.075) for timing in reasonable_timings_order[:-1]])
                timing_minus_chosen = total_timing - timing_order_minus_maple_call
                #if total_timing>4:
                #    print(timing_minus_maple_call)
            else:
                timing_minus_chosen = total_timing
            timings_minus_chosen.append(timing_minus_chosen)
        
        return timings_minus_chosen

    def get_ncells(self):
        '''
        Returns the number of cells of its possible CADs depending on the ordering.
        '''
        return [cad.ncells for cad in self.get_possible_CADs()]

    def get_all_projections(self):
        '''
        Returns the projections of its possible CADs depending on the ordering.
        '''
        all_projections = [cad.projected_polynomials for cad in self.get_possible_CADs()]
        return all_projections


        

    def get_max_degrees(self):
        '''This function will return a list of the maximum degree of each variable'''
        return [max(elem) for elem in zip(*[monomial[:-1] for polynomial in self.polynomials for monomial in polynomial.matricial_form ])]

    def get_prop_variables_in_polynomials(self):
        '''This function will return a list of the proportion of polynomials in which each variable appears'''
        return [sum(elem)/len(elem) for elem in zip(*[polynomial.used_variables for polynomial in self.polynomials])]

    def get_prop_variables_in_monomials(self):
        '''This function will return a list of the proportion of monomials in which each variable appears'''
        return [sum(elem)/len(elem) for elem in zip(*[monomial[:-1] for polynomial in self.polynomials for monomial in polynomial.matricial_form ])]

    def dorians_features(self):
        '''This function will return the 11 characteristics of described in Dorian's paper of a problem'''
        characteristics = []
        characteristics.append(len(self.polynomials)) # the number of polynomials is added
        characteristics.append(max([polynomial.max_degree for polynomial in self.polynomials])) # the maximum total degree of polynomials
        characteristics += self.get_max_degrees() # the maximum degree of each variable among the polynomials
        characteristics += self.get_prop_variables_in_polynomials() # the proportion of polynomials containing each variable
        characteristics += self.get_prop_variables_in_monomials() # the proportion of monomials containing each variable
        return characteristics

    def get_projections(self):
        try:
            return self.projections
        except AttributeError:
            self.projections, self.degrees_for_heuristics = recurrent_project([polynomial.matricial_form for polynomial in self.polynomials], return_for_heuristics = True)
        return self.projections

    def get_degrees_for_heuristics(self):
        try:
            return self.degrees_for_heuristics
        except AttributeError:
            self.projections, self.degrees_for_heuristics = recurrent_project([polynomial.matricial_form for polynomial in self.polynomials], return_for_heuristics = True)
        return self.degrees_for_heuristics

    def return_with_projections(self):
        '''This function will return the same object with the projections added'''
        self.projections, self.degrees_for_heuristics = recurrent_project([polynomial.matricial_form for polynomial in self.polynomials], return_for_heuristics = True)
        if any([999999 in lst for lst in self.degrees_for_heuristics]):
            print(self.file)
        return self

    def sotd_guess(self):
        '''Computes the best order according to the sotd heuristic proposed by Dolzmann et al.'''
        sotd_values = [possible_CAD.sotd() for possible_CAD in self.get_possible_CADs()] # sum of the total degrees of all monomials in all polynomials in the full projection set
        return min(range(len(sotd_values)), key=sotd_values.__getitem__) # returns the index with the smalles value in the list sotd_values

    def mods_guess(self):
        '''Computes the best order according to the mods heuristic (multiplication of relative degrees).'''
        mods_values = [possible_CAD.mods() for possible_CAD in self.get_possible_CADs()]
        return min(range(len(mods_values)), key=mods_values.__getitem__) # returns the index with the smalles value in the list mods_values

    def logmods_guess(self):
        '''Computes the best order according to the logmods heuristic (multiplication of the logarithm of relative degrees).'''
        logmods_values = [possible_CAD.logmods() for possible_CAD in self.get_possible_CADs()]
        return min(range(len(logmods_values)), key=logmods_values.__getitem__) # returns the index with the smalles value in the list logmods_values

    def acc_mods_guess(self):
        '''Computes the best order according to the mods heuristic (multiplication of relative degrees).'''
        acc_mods_values = [possible_CAD.acc_mods() for possible_CAD in self.get_possible_CADs()]
        return min(range(len(acc_mods_values)), key=acc_mods_values.__getitem__) # returns the index with the smalles value in the list mods_values

    def acc_logmods_guess(self):
        '''Computes the best order according to the logmods heuristic (multiplication of the logarithm of relative degrees).'''
        acc_logmods_values = [possible_CAD.acc_logmods() for possible_CAD in self.get_possible_CADs()]
        return min(range(len(acc_logmods_values)), key=acc_logmods_values.__getitem__) # returns the index with the smalles value in the list logmods_values

    def greedy_sotd_guess(self):
        '''Computes the best order according to the greedy sotd heuristic.'''
        sotds_in_levels = [possible_CAD.sotd_in_levels() for possible_CAD in self.get_possible_CADs()]
        minimal_greedy_sotd = sotds_in_levels[0]
        minimal_index = 0
        for index, one_sotd in enumerate(sotds_in_levels):
            if first_vector_is_smaller_or_equal(one_sotd, minimal_greedy_sotd):
                minimal_greedy_sotd = one_sotd
                minimal_index = index
        return minimal_index

    def greedy_mods_guess(self):
        '''Computes the best order according to the greedy mods heuristic.'''
        projections = [cad.projected_polynomials for cad in self.get_possible_CADs()]
        return order_given_projections(projections, heuristic="greedy_mods")

    def greedy_logmods_guess(self):
        '''Computes the best order according to the greedy mods heuristic.'''
        projections = [cad.projected_polynomials for cad in self.get_possible_CADs()]
        return order_given_projections(projections, heuristic="greedy_logmods")

    def brown_guess(self):
        '''Computes the best order according to a simplified brown heuristic.'''
        projections = [cad.projected_polynomials for cad in self.get_possible_CADs()]
        return order_given_projections(projections, heuristic="brown")

    def create_similar_polynomials(self, possible_coeffs, possible_degrees, possible_nterms, possible_used_variables, procedure:int=4, max_nvar:int=3):

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
        polynomials = self.create_similar_polynomials(procedure, possible_coeffs, possible_degrees, possible_nterms, possible_used_variables)
        return CADProblem(polynomials, self.subdir+"_synthetic_"+str(procedure), self.file+"_synthetic_"+str(procedure), with_projections=True)

    def dataset_info(self, features_type:str="projections", target_type:str="multiclass", return_timings:bool=False, return_heuristics_costs:bool=False, return_ncells:bool=False): 

        if features_type == "Dorian":
            feature = self.dorians_features()
        elif features_type == "projections":
            feature = self.get_all_projections()
        else:
            raise Exception("No features type called " + features_type)

        if target_type == "binary_multiclass":
            target = [int(timing==min([timing if type(timing)!=str else Inf for timing in self.get_timings()])) for timing in self.get_timings()] # will return a vector of vectors with one(s) in the fastest position and ceros in the rest
        if target_type == "multiclass":
            target = [int(timing==min([timing if type(timing)!=str else Inf for timing in self.get_timings()])) for timing in self.get_timings()].index(1) # will return a vector of the integers representing the fastest position on each problem
        else:
            raise Exception("No target type called " + target_type)
        
        if return_timings:
            min_timing = self.get_timings()
            
            if return_heuristics_costs:
                heuristics_cost = self.get_times_invested_in_projection()

                if return_ncells:
                    ncells = self.get_ncells()
                    return feature, target, min_timing, heuristics_cost, ncells
                else:
                    return feature, target, min_timing, heuristics_cost
            else:
                return feature, target, min_timing
        else:
            return feature, target

class CADFolder:
    def __init__(self, problems:list, subdir: str = None, file: str = None) -> None:
        print(problems)
        if problems != None:
            self.subdir = subdir
            self.file = file
            self.problems = problems
            self.nproblems = len(problems)

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

    def get_deep_problems(self, min_nvar:int=3, max_nvar:int=3, without_repetition=False):
        '''This function will return all the problems satisfying the properties inside this folder and of the folders inside this folder recursively'''
        problems = []
        for elem in self.problems:
            if type(elem) == CADProblem and elem.nvariables>=min_nvar and elem.nvariables<=max_nvar:
                if without_repetition:
                    if elem.get_ncells() not in [problem.get_ncells() for problem in problems]:
                        problems += [elem]
                else:
                    problems += [elem]
            elif type(elem) == CADFolder:
                problems += elem.get_deep_problems(min_nvar=min_nvar, max_nvar=max_nvar, without_repetition=without_repetition)
        return problems

    def get_repeated_problems(self):
        n_without_rep = 0
        n_difficult_problems = 0
        problems = self.get_deep_problems()
        print(len(problems))
        ncells_problems = [[cad.ncells for cad in problem.possible_CADs] for problem in problems]
        while ncells_problems != []:
            n_without_rep += 1
            ncells = ncells_problems[0]
            repetitions = ncells_problems.count(ncells)
            if repetitions > 9:
                if all([type(ncell)==str for ncell in ncells]):
                    n_difficult_problems+=repetitions
                    print("There is a problem repeated ", repetitions, " times, in which for the different orders the number of cells are ", ncells)
                else:
                    print("There is a problem repeated ", repetitions, " times, in which for the different orders the number of cells are ", ncells)
            ncells_problems = list(filter(lambda a: a!=ncells, ncells_problems))
        print("Number of difficult problems: ", n_difficult_problems)
        print("Number of unique problems: ", n_without_rep)

    def info_for_synthetic_data(self):
        possible_coeffs = self.get_coeffs()
        possible_degrees = self.get_degrees()
        possible_nterms = self.get_nterms()
        possible_used_variables = self.get_used_variables()
        possible_problems = [problem for problem in self.problems if problem.polynomials != []]
        return possible_coeffs, possible_degrees, possible_nterms, possible_problems, possible_used_variables

    def infinite_dataset_synthetic(self, output_location, procedure:int=4):
        possible_coeffs, possible_degrees, possible_nterms, possible_problems, possible_used_variables = self.info_for_synthetic_data()
        dataset = []
        while True:
            print(len(possible_problems))
            chosen_problem = random.choice(possible_problems)
            new_polynomials = chosen_problem.create_similar_polynomials(possible_coeffs, possible_degrees, possible_nterms, possible_used_variables, procedure=procedure, max_nvar=3)
            print("NEW POLYS \n")
            print(new_polynomials)
            new_problem = CADProblem(new_polynomials, with_projections=True)
            if not all([type(timing)==str for timing in new_problem.get_timings()]):
                new_data = new_problem.dataset_info()
                print("NEW DATA \n")
                print(new_data)
                dataset.append([new_data])
                f = open(output_location, "wb")
                pickle.dump(dataset, f)
                f.close()

    def transform_to_dataset(self, features_type:str="Dorian", target_type:str="multiclass", return_timings:bool=False, return_heuristics_costs:bool=False, return_ncells:bool=False, without_repetition=False): # add an option to exclude all the times out, and to handle the times in with times out
        '''This function will return a dataset of the problems on it with the desired features and objectives.'''

        problems = [problem for problem in self.get_deep_problems() if not all([type(timing)==str for timing in problem.get_timings()]) and len(problem.get_timings())==math.factorial(problem.nvariables)] # the problems in which all the orders timed out are removed

        if without_repetition:
            problems = remove_repeated(problems)
        
        if return_timings:
            
            if return_heuristics_costs:

                if return_ncells:
                    features, targets, min_timings, heuristics_costs, ncells = zip(*[problem.dataset_info(features_type=features_type, target_type=target_type, return_timings=return_timings, return_heuristics_costs=return_heuristics_costs, return_ncells=return_ncells) for problem in problems])
                    print(ncells)
                    return list(features), list(targets), list(min_timings), list(heuristics_costs), list(ncells)
                else:

                    features, targets, min_timings, heuristics_costs = zip(*[problem.dataset_info(features_type=features_type, target_type=target_type, return_timings=return_timings, return_heuristics_costs=return_heuristics_costs, return_ncells=return_ncells) for problem in problems])
                    return list(features), list(targets), list(min_timings), list(heuristics_costs)
            else:
                features, targets, min_timings = zip(*[problem.dataset_info(features_type=features_type, target_type=target_type, return_timings=return_timings, return_heuristics_costs=return_heuristics_costs, return_ncells=return_ncells) for problem in problems])
                return list(features), list(targets), list(min_timings)
        else:
            features, targets = zip(*[problem.dataset_info(features_type=features_type, target_type=target_type, return_timings=return_timings, return_heuristics_costs=return_heuristics_costs, return_ncells=return_ncells) for problem in problems])
            return list(features), list(targets)

        

        print("There have been found "+str(len(self.get_deep_problems())-len(problems))+"problems that timeout for all orderings. Out of "+str(len(self.get_deep_problems())))

        if features_type == "Dorian":
            features = [problem.dorians_features() for problem in problems]
        elif features_type == "projections":
            features = [problem.get_all_projections() for problem in problems]
        else:
            raise Exception("No features type called " + features_type)

        if target_type == "binary_multiclass":
            targets = [[int(timing==min([timing if type(timing)!=str else Inf for timing in problem.get_timings()])) for timing in problem.get_timings()] for problem in problems] # will return a vector of vectors with one(s) in the fastest position and ceros in the rest
        if target_type == "multiclass":
            targets = [[int(timing==min([timing if type(timing)!=str else Inf for timing in problem.get_timings()])) for timing in problem.get_timings()].index(1) for problem in problems] # will return a vector of the integers representing the fastest position on each problem
        else:
            raise Exception("No target type called " + target_type)
        
        if return_timings:
            min_timings = [problem.get_timings() for problem in problems]
            
            if return_heuristics_costs:
                heuristics_costs = [problem.get_times_invested_in_projection() for problem in problems]

                return features, targets, min_timings, heuristics_costs
            else:
                return features, targets, min_timings
        else:
            return features, targets

    def split_train_test(self, test_size, separate_repeated:bool=True, return_timings:bool=False, random_seed:int=0):
        '''
        This function will return the same as train_test_split in sklearn but making sure that two problems with the same features fall in the same category, either train or test.
        If you ask to return_timings then the list of the timings for test and train instances is returned.
        '''
        random.seed(random_seed)
        if return_timings == True:
            features, target, timings = self.transform_to_dataset(return_timings=True)
        else:
            features, target = self.transform_to_dataset(return_timings=False)
        ntest = len(features)*test_size # the number of problems used for testing
        features_test = []
        target_test = []
        timings_test = []
        while len(features_test) < ntest: # we want at least this amount of testing instances
            j = random.randrange(len(features))
            if separate_repeated: # if we want to separate all the problems with repeated features we go through all of them, and if they share the features then put them in the test set
                new_features = features[j]
                for i in range(len(features)-1,-1,-1):
                    if features[i]==new_features:
                        features_test.append(features.pop(i))
                        target_test.append(target.pop(i))
                        if return_timings:
                            timings_test.append(timings.pop(i))
            else:
                features_test.append(features.pop(j))
                target_test.append(target.pop(j))
                if return_timings:
                    timings_test.append(timings.pop(j))
        features_train = features
        target_train = target
        timings_train = timings
        if return_timings:
            return features_train, features_test, target_train, target_test, timings_train, timings_test
        else:
            return features_train, features_test, target_train, target_test
            

    def add_projections(self):
        '''This function will return an object equal to this but with all the projections of its problems computed'''
        return CADFolder([problem.return_with_projections() for problem in self.get_deep_problems()], self.subdir, self.file)