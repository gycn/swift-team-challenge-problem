#!/bin/bash
# Usage: run_experiment.sh [data directory] [xlen] [ylen] [timesteps] [output timesteps] [output directory] [ground truth image directory]
# Phase One: Perform offline inference on first n frames to get parameters

# Make BLOG file, load images and means from pre-processing to Swift-readable text format
python util/make_blog_file.py --input_name templates/bsub_offline_learn_param.blog --output_name swift/example/bsub_offline.blog --query_type offline_param -t $4 --xlen $2 --ylen $3
python util/make_param_txt.py --input_dir . --data_dir $1 --num_timesteps $4 --query_type read_img_sequence
mv data_*.txt swift/src
mv means.txt swift/src/means_init.txt

# Run offline Metropolis-Hastings to get mean and covariance parameters for each pixel
cd swift
./swift -e MHSampler -n 10000005 --burn-in 10000000 -i example/bsub_offline.blog -o src/bsub_offline.cpp 
cd src
g++ -Ofast -std=c++11 bsub_offline.cpp random/*.cpp -o bsub_offline -larmadillo
./bsub_offline > bsub_output.txt
mv bsub_output.txt ../../
cd ../../

# Parse means/covariances from output file and prepare parameters for Phase Two
python util/parse_output_file.py --input_file bsub_output.txt --output_dir mean_var_temp --query_type mean_var_offline --xlen $2 --ylen $3
python util/make_param_txt.py --input_dir mean_var_temp
cp mean_var_temp/means.txt mean_var_temp/vars.txt swift/src/


# Phase Two: Load means/variances as initialization and getting output labels

# Make labeling scheme BLOG file 
python util/make_blog_file.py --input_name templates/bsub_offline_label.blog --output_name swift/example/bsub_offline_label.blog --query_type offline_label -t $5 --xlen $2 --ylen $3
cd swift
./swift -e MHSampler -n 80000005 --burn-in 80000000 -i example/bsub_offline_label.blog -o src/bsub_offline_label.cpp
cd src
g++ -Ofast -std=c++11 bsub_offline_label.cpp random/*.cpp -o bsub_offline_label -larmadillo
./bsub_offline_label > bsub_output_label.txt
mv bsub_output_label.txt ../../
cd ../../

# Parse labels from output log into images
mkdir $6
python util/parse_output_file.py --input_file bsub_output_label.txt --output_dir $6 --query_type offline_sequence --xlen $2 --ylen $3


# Phase Three: Evaluation
python evaluation/labeled_image_to_mat.py -f $7 -o $6/gt_mat -b 0
python evaluation/labeled_image_to_mat.py -f $6/blog -o $6/blog_mat -b 0

python evaluation/evaluate_mats.py -p $6/blog_mat -t $6/gt_mat -g True -o ../
