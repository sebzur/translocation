#! /bin/bash
#c=$1
#for e in `LC_CTYPE="en_EN.UTF-8" seq 100 500 25000`
#for period in `LC_CTYPE="en_EN.UTF-8" seq 50 100 2000`
for N in 10 15 20 30 50
    do
        for eps in 0.01 0.5  2  5  10 
	do
	    mpirun -n 16  python mpiruns.py -n $N -s 1000000 -r 32 -c 0.5 -e $eps --path "/home/seba/WYNIKI_TRANS/ion"
	done
    done
