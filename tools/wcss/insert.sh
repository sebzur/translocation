#!/bin/bash
#PBS -l select=40:ncpus=1:mpiprocs=1
#PBS -q normal
#PBS -l software=chain_translocation_C_2_N
# ---PBS -software translocate_"$N"_"$s"_"$eps"_"$c"
# i tak dalej
cd ~/git/translocation/polymer
mpiexec -n 40 /usr/local/zgoraphysics/bin/python2.7 reptation.py -p $N -s $s -r 80 -e $eps -l 1 -o ~/TRANS/ >> ~/TRANS/rept_out.err >> ~/TRANS/rept_out.out