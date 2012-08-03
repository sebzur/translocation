#! /bin/bash
for eps in `LC_CTYPE="en_EN.UTF-8" seq 10 2 100`
   do
    PYTHONPATH=$PYTHONPATH:/storage/software/git/KMC/ mpirun -n 4 python example.py  --runs 4 --steps 10000 -p $eps -l 1 -d 2 -e 0.01
   done