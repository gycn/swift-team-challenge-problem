#!/bin/bash
# Update and install armadillo/swift dependencies
sudo apt-get update
sudo apt-get install git g++ cmake libopenblas-dev liblapack-dev libarpack++2-dev
sudo apt-get install python-numpy python-scipy python-skimage
# Extract, configure and install armadillo
wget http://sourceforge.net/projects/arma/files/armadillo-7.400.2.tar.xz
tar xvf armadillo-7.400.2.tar.xz
cd armadillo-7.400.2
cmake .
make
sudo make install
cd ..
rm armadillo-7.400.2.tar.xz
# Clone and compile swift
git clone https://github.com/lileicc/swift.git
cd swift
git pull origin quantify-query-experimental:quantify-query-experimental
git checkout quantify-query-experimental
make compile
cd ..

# Current TCP setup with repo
# git clone https://github.com/giulio-zhou/swift-team-challenge-problem.git 
# mv swift swift-team-challenge-problem
# cd swift-team-challenge-problem
