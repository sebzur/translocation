#!/bin/bash
#PBS -l select=40:ncpus=1:mpiprocs=1
#PBS -q normal
#PBS -l software=chain_translocation_C_2_N
# ---PBS -software translocate_"$N"_"$s"_"$eps"_"$c"
# i tak dalej
cd ~/git/translocation/polymer
mpiexec -n 40 /usr/local/zgoraphysics/bin/python2.7 realistic.py -p $N -s $s -r 40 -e $eps -l 1 -b 0.005 -c 0.005 -k 0.3 -x 0.5 -o ~/DRIFT/ >> ~/DRIFT/rept_out.err >> ~/DRIFT/rept_out.out