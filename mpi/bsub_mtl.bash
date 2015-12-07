#!/bin/sh
#BSUB -J mtl_downscaling
#BSUB -o mtl_results
#BSUB -e error_mtl_downscaling
#BSUB -n 100
#BSUB -q ser-par-10g-3
#BSUB -cwd /home/vandal.t/repos/pydownscale/mpi
######## THIS IS A TEMPLATE FILE FOR TCP ENABLED MPI RUNS ON THE DISCOVERY CLUSTER ########
#### #BSUB -n has a value equal to the given value for the -np option ####
# prefix for next run is entered below
# file staging code is entered below

#### Enter your working directory below - this is the string returned from issuing the command 
#### "pwd"
#### IF you stage your files this is your run directory in the high speed scratch space mounted 
#### across all compute nodes
work=/home/vandal.t/repos/pydownscale/mpi
#####################################################
########DO NOT EDIT ANYTHING BELOW THIS LINE#########
#####################################################
cd $work
tempfile1=hostlistrun2
tempfile2=hostlist-tcp2
echo $LSB_MCPU_HOSTS > $tempfile1
declare -a hosts
read -a hosts < ${tempfile1}
for ((i=0; i<${#hosts[@]}; i += 2)) ; 
do 
   HOST=${hosts[$i]}
   CORE=${hosts[(($i+1))]} 
   echo $HOST:$CORE >> $tempfile2
done
#####################################################
########DO NOT EDIT ANYTHING ABOVE THIS LINE#########
#####################################################
###### Change only the -np option giving the number of MPI processes and the executable to use 
###### with options to it
###### IN the example below this would be "8", "helloworld.py" and the options for the executable 
###### DO NOT CHANGE ANYTHING ELSE BELOW FOR mpirun OPTIONS
###### MAKE SURE THAT THE "#BSUB -n" is equal to the "-np" number below. IN this example it is 8.

# source /shared/apps/sage/sage-5.12/spkg/bin/sage-env
mpirun -np 100 -prot -TCP -lsf /home/vandal.t/repos/pydownscale/mpi_mtl.py
# any clean up tasks and file migration code is entered below

#####################################################
########DO NOT EDIT ANYTHING BELOW THIS LINE#########
#####################################################
rm $work/$tempfile1
rm $work/$tempfile2
#####################################################
########DO NOT EDIT ANYTHING ABOVE THIS LINE#########
#####################################################
