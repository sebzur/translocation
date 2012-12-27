#!/bin/bash
N=$1
s=$2
for k in 4.60517 3.21887 1.38629 0.21072
#for N in `LC_CTYPE="en_EN.UTF-8" seq 40 15 55`
do
    qsub -v k=${k} insert_correlation.sh
done
