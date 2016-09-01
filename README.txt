==================
   Instructions
==================
The setup and execution instructions listed in this README have been tested
and verified to work on an Amazon EC2 Ubuntu 14.04 with the following specs:
  * 30GB of disk space
  * 32GB of RAM
  * 8 vCPU's
Specifically, the instance used was an m4.2xlarge with the description
"Ubuntu Server 14.04 LTS (HVM), SSD Volume Type - ami-d732f0b7".

To install the armadillo, BLOG and Python dependencies, run the setup script.
    ./setup.sh
To run an end-to-end BLOG example, execute the run_experiment script.
    ./run_experiment.sh [data directory] [xlen] [ylen] [timesteps] [output timesteps] [output directory]
