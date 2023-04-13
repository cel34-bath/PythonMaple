import sys
sys.path.append('./')
from WorkWithMaple.polynomials.polynomial_objects import Polynomial, Problem, Folder

p0 = Polynomial([[1,5,3],[1,3,1],[1,0,3]])
p1 = Polynomial([[0,5,3],[0,3,1],[0,3,3]])
p2 = Polynomial([[4,2,6],[3,5,-1],[1,1,32]])
prb1 = Problem([p0,p1])
prb2 = Problem([p2,p1])
print(prb1.get_degrees())
print(prb1.univariates_nroots())
print(prb2.get_degrees())
print(prb2.univariates_nroots())
fld = Folder([prb1, prb2])
print(fld.univariates_nroots())
print(fld.univariates_nroots_degree_n(5))