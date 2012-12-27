#!/bin/bash
#PBS -l select=40:ncpus=1:mpiprocs=1
#PBS -q normal
#PBS -l software=chain_translocation_C_2_N
# ---PBS -software translocate_"$N"_"$s"_"$eps"_"$c"
# i tak dalej
cd ~/git/translocation/polymer
mpiexec -n 40 /usr/local/zgoraphysics/bin/python2.7 realistic.py -p 400 -s 20000000 -r 40  -l 1 -b 0.5 -c 0.5 -k $k -x 4.6051 -z 100 -o ~/DRIFT2/ >> ~/DRIFT2/rept_out.err >> ~/DRIFT2/rept_out.out