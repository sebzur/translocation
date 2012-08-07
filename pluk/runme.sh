#!/bin/bash
for len in `LC_CTYPE="en_EN.UTF-8" seq 10 15 100`
do
    for eps in `LC_CTYPE="en_EN.UTF-8" seq 0.1 0.1 0.1`
    do
	PYTHONPATH=$PYTHONPATH:/home/seba/codebase/git/KMC/ mpirun -n 44 --hostfile hostfile python example.py  --runs 44 --steps 1000000 -n $len -l 1 -d 2 -e $eps -b 0.5 -c 0.5
    done
done
