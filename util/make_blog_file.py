import argparse
import numpy as np
import os
import shutil
import skimage.io as skio

parser = argparse.ArgumentParser(
    description="Read frames from input file and generate BLOG file"
                "for background subtraction.") 
parser.add_argument('--input_name', default='bsub.dblog',
    help="Name of input template file (default: bsub.dblog)")
parser.add_argument('--output_name', default='output_blog.dblog',
    help="Name of output BLOG file (default: output_blog.dblog)")
parser.add_argument('--query_type', default='label',
    help="Type of query (label, mean, etc)")
parser.add_argument('-t', type=int, help="Number of timesteps")
parser.add_argument('--xlen', type=int, help="X dimension")
parser.add_argument('--ylen', type=int, help="X dimension")
args = parser.parse_args()

type_declarations = "type Component;\n" \
                    "type ImageX;\n" \
                    "type ImageY;\n" \
                    "type Time;\n"
number_format = "distinct Component Component[{0}];\n" \
                "distinct ImageX ImageX[{1}];\n" \
                "distinct ImageY ImageY[{2}];\n" \
                "distinct Time Time[{3}];\n" \
                "fixed Integer xdim = {1};\n" \
                "fixed Integer ydim = {2};\n" \
                "fixed Integer numTimesteps = {3};\n"

def add_header(output_file):
    output_file.write(type_declarations)
    output_file.write(number_format.format(3, args.xlen, args.ylen, args.t))

def add_prev_offline(output_file, t):
    output_file.write('fixed Time prevTime(Time t) =\n')
    output_file.write('    case t in {\n')
    output_file.write('        Time[0] -> Time[0],\n')
    for i in range(1, t):
        output_file.write('        Time[%d] -> Time[%d],\n' % (i, i - 1))
    output_file.write('        Time[%d] -> Time[%d]\n' % (t, t - 1))
    output_file.write('    };\n\n')


def main():
    output_file = open(args.output_name, 'w')
    add_header(output_file)
    with open(args.input_name, 'r') as input_file:
        output_file.write(''.join(input_file.readlines()))
    output_file.close()


if __name__ == '__main__':
    main()
