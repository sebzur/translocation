#!/bin/bash                                                                                                                                                                        
for eps in `LC_CTYPE="en_EN.UTF-8" seq 0.4 0.1 3.0`
do
    PYTHONPATH=$PYTHONPATH:/home/seba/codebase/git/KMC/:/home/seba/codebase/git/translocation/ mpirun -n 16  python reptation.py  --runs 16 --steps 5000000 -p 100 -l 1 -e $eps -b 0.5 -c 0.5 -k 0.1 -x 0.1 -o /home/seba/TRANSLOCATION/
done

