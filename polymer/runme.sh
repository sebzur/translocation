#!/bin/bash
for len in `LC_CTYPE="en_EN.UTF-8" seq 100 15 150`
do
    for eps in `LC_CTYPE="en_EN.UTF-8" seq 0.1 0.1 0.1`
    do
	PYTHONPATH=$PYTHONPATH:/home/seba/codebase/git/KMC/:/home/seba/codebase/git/translocation/ mpirun -n 44 --hostfile hostfile python example.py  --runs 44 --steps 4000000 -p $len -l 1 -e $eps -b 0.5 -c 0.5 -o /home/seba/TRANSLOCATION
    done
done
