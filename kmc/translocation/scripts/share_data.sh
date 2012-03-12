#! /bin/bash
for len in {1..1}
do
 scp -r ../../../kmc seba@192.168.44.14$len:~/codebase
done

