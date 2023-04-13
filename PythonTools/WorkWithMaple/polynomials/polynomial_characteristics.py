import os
import sys
from collections import Counter

cwd = os.getcwd()
if "Repositories" in cwd:
    initial_directory = cwd.split("Repositories")[0]+"Repositories"
else:
    raise Exception("You're too far from Repositories.")
    
sys.path.append('./') #This means to start looking in the same directory you're running
#if __name__ == '__main__':
#    import sys
#    sys.path.append(os.getcwd())


def number_of_terms(polynomial:list=[]):
    '''This function counts the number of terms of a polynomial given in matricial form'''

    degrees = [monomial[:-1] for monomial in polynomial]
    unique_degrees = []
    coefficients = []
    for monomial in polynomial:
        if monomial[:-1] not in unique_degrees:
            unique_degrees.append(monomial[:-1])
            coefficients.append(monomial[-1])
        else:
            coefficients[unique_degrees.index(monomial[:-1])] += monomial[-1]

    return len([coeff for coeff in coefficients if coeff!=0])
