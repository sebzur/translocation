#!/bin/bash
eps=$1
s=$2
for N in `LC_CTYPE="en_EN.UTF-8" seq 40 15 150`
#for N in `LC_CTYPE="en_EN.UTF-8" seq 40 15 55`
do
    qsub -v N=${N},eps=${eps},s=${s} insert.sh
done
