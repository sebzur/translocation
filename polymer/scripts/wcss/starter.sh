#!/bin/bash
eps=$1
s=$2
for N in `LC_CTYPE="en_EN.UTF-8" seq 55 15 175`
do
    qsub -v N=${N},eps=${eps},s=${s} insert.sh
done
