#!/bin/bash
for len in `LC_CTYPE="en_EN.UTF-8" seq 20 15 150`
do
    for eps in `LC_CTYPE="en_EN.UTF-8" seq 0.001 0.001 0.001`
    do
	PYTHONPATH=$PYTHONPATH:/home/seba/codebase/git/KMC/:/home/seba/codebase/git/translocation/ mpirun -n 40 --hostfile hostfile python reptation.py  --runs 40 --steps 4000000 -p $len -l 1 -e $eps -o /home/seba/TRANSLOCATION
    done
done
