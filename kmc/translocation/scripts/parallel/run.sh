#!/bin/bash
N=$1
c=$2
s=$3
#for eps in 0.01 0.5 1 2 3.5 5 7 10 20 30
for eps in 0.01 0.5 1 2 3.5 5 7 10 20 30
do
    qsub -v N=${N},eps=${eps},s=${s},c=${c} insert.sh
done
