#!/bin/bash
#PBS -l select=36:ncpus=12:mpiprocs=12
#PBS -q normal
#PBS -l software=chain_translocation_C_2_N
# ---PBS -software translocate_"$N"_"$s"_"$eps"_"$c"
# i tak dalej
cd ~/git/translocation/polymer
mpiexec -n 36 /usr/local/zgoraphysics/bin/python2.7 realistic.py -p $N -s $s -r 40 -e $eps -l 1 -b 0.005 -c 0.005 -k 0.1 -x 0.1 -o ~/DRIFT/ >> ~/DRIFT/rept_out.err >> ~/DRIFT/rept_out.out