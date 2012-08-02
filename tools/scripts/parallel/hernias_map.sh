#!/bin/bash
length=$1
for N in 12 20 50 100
    do
        for eps in 0.01 0.5 1 2 3.5 5 7 10 20 30
	do
            for c in 0.02 0.05 1
	    do
		mpiexec -n 32 --hostfile /home/seba/codebase/kmc/translocation/scripts/parallel/hostfile python /home/seba/codebase/kmc/translocation/scripts/mpiruns.py -n $N -s $length -r 80 -c $c -e $eps 2>>/home/seba/codebase/kmc/translocation/scripts/results/output.err >> /home/seba/codebase/kmc/translocation/scripts/results/output.out	    
	    done
	done
    done
