#! /bin/bash
#for e in `LC_CTYPE="en_EN.UTF-8" seq 100 500 25000`
steps=$1
r=$2
for N in `LC_CTYPE="en_EN.UTF-8" seq 5 1 $r`
do
   python singlerun.py $N 2 $steps
done
