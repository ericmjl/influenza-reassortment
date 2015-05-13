#!/bin/sh
#$ -S /bin/sh
#$ -cwd
#$ -V
#$ -m e
#$ -M ericmjl@mit.edu
#$ -pe whole_nodes 1
#############################################

python preprocessing.py "20141103 All IRD"