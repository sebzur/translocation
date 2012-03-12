import numpy

n = 13 # ~ Liczba bp w porze
U = 600 * 10**-3 # roznica potencjalow
L = 5 * 10**-9 # grubosc pora

e = 1.6 * 10**-19 
Kb = 1.38 * 10**-23
T = 300 

print ((n * e) * U * L)/Kb * T
