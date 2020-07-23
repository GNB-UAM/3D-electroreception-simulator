#!/bin/bash
#
#$ -S /bin/bash
#$ -cwd
#$ -o mpirun.out
#$ -j y
#$ -pe mpi ${workers}
#$ -q mpi.q

PATH=/home/${user}/opt/gmsh4/bin/:$PATH mpirun -np $NSLOTS /share/apps/miniconda/bin/python3.7 main.py --qsub ${opt}