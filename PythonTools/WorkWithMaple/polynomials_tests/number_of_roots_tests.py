#import pytest
import os
##import detect
##
##if detect.linux:
##    initial_directory = os.path.join( "/home", "delriot", "Documents", "Repositories")
##elif detect.windows:
##    initial_directory = os.path.join( "C:\\", "Users", "teres", "OneDrive - Coventry University", "Repositories")

#if __name__ == '__main__':
#    import sys
#    sys.path.append(os.getcwd())

##import sys
##sys.path.append('./')
from ..polynomials.polynomial_characteristics import number_of_roots_by_maple


def test_some_sets_of_polynomials():
    polynomial_set0 = []
    assert number_of_roots_by_maple(polynomial_set0) == []
    polynomial_set1 = [[[1,1]]]
    assert number_of_roots_by_maple(polynomial_set1) == [1]
    polynomial_set2 = [[[3,-1],[2,1],[0,1]],[[2,1],[0,-1]]]
    assert number_of_roots_by_maple(polynomial_set2) == [1,2]


test_some_sets_of_polynomials()
