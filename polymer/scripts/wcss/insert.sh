#!/bin/bash
#PBS -l select=40:ncpus=1:mpiprocs=1
#PBS -q normal
#PBS -l software=chain_translocation_C_2_N
# ---PBS -software translocate_"$N"_"$s"_"$eps"_"$c"
# i tak dalej
cd /home/sebzur/git/translocation/pluk
mpiexec -n 40 /usr/local/zgoraphysics/bin/python2.7 example.py -n $N -s $s -r 160 -e $eps -l 1 -d 2 >>scripts/wcss/output.err >> scripts/wcss/output.out	    


