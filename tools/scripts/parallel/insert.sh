#!/bin/bash
#PBS -l select=40:ncpus=1:mpiprocs=1:mem=4096MB
#PBS -q parallel
#PBS -l software=chain_translocation_C_3_N_325
# ---PBS -software translocate_"$N"_"$s"_"$eps"_"$c"
# i tak dalej
cd /home/sebzur/kmc
mpiexec -n 40 /usr/local/zgoraphysics/bin/python2.7 translocation/scripts/mpiruns.py -n $N -s $s -r 80 -c $c -e $eps 2>>translocation/scripts/results/output.err >> translocation/scripts/results/output.out	    


