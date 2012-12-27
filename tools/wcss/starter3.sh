#!/bin/bash
N=$1
s=$2
for eps in `LC_CTYPE="en_EN.UTF-8" seq 0.1 0.2 10`
#for N in `LC_CTYPE="en_EN.UTF-8" seq 40 15 55`
do
    qsub -v N=${N},eps=${eps},s=${s} insert_drift3.sh
done
