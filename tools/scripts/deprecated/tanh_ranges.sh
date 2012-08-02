#! /bin/bash
#c=$1
#for e in `LC_CTYPE="en_EN.UTF-8" seq 100 500 25000`
#for period in `LC_CTYPE="en_EN.UTF-8" seq 50 100 2000`
for N in 9 10
    do
        for eps in 0.01 0.5 1 5 10 20 30
	do
            python tanh_thread.py $N $eps 50000 64 16
	done
    done
