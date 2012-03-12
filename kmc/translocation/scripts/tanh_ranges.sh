#! /bin/bash
#c=$1
#for e in `LC_CTYPE="en_EN.UTF-8" seq 100 500 25000`
#for period in `LC_CTYPE="en_EN.UTF-8" seq 50 100 2000`
for N in 12 15 17 20 25 50 75 100 150 200 250 300
    do
        for eps in 0.01 0.5 1 2 3.5 5 7 10 20 30
	do
	    mpirun -n 29 --hostfile hostfile python mpiruns.py -n $N -s 1000000 -r 29 -c 0.0 -e $eps
	done
    done
