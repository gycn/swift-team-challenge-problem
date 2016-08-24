import argparse
import numpy as np
import os
import re
import skimage
import skimage.io as skio

parser = argparse.ArgumentParser(
    description="Read in output of BLOG program and"
                "convert to image sequence.")
parser.add_argument('--input_file',
    help="File name of input file to be parsed")
parser.add_argument('--output_dir',
    help="Name of output directory for video sequence")
parser.add_argument('--query_type',
    help="Name of desired query")
parser.add_argument('--xlen', type=int,
    help="Width of input images")
parser.add_argument('--ylen', type=int,
    help="Height of input images")
args = parser.parse_args()

def parse_mean_var_offline():
    imgs = []
    cov_mat = []
    f = open(args.input_file, 'r')
    state, x, y = None, None, None
    re_com = re.compile('Component\[([0-9]+)\]')
    re_imx = re.compile('ImageX\[([0-9]+)\]')
    re_imy = re.compile('ImageY\[([0-9]+)\]')
    curr_val = []
    for line in f.readlines():
        contents = line.split()
        if 'query' in line:
            comp = int(re_com.findall(line)[0])
            x = int(re_imx.findall(line)[0])
            y = int(re_imy.findall(line)[0])
            if 'Mean' in line:
                state = 'mean'
            elif 'Variance' in line:
                state = 'var'
            if comp >= len(imgs):
                for i in range(len(imgs), comp + 1):
                    imgs.append(np.zeros((args.ylen, args.xlen, 3)))
                    cov_mat.append(np.zeros((args.xlen, args.ylen, 3, 3)))
        elif 'DiagVar' in line:
            if state == 'mean':
                imgs[comp][y, x] = np.array(curr_val)
            elif state == 'var':
                cov_mat[comp][y, x] = np.array(curr_val)
            curr_val = []
            state = None
        elif ('loopend' in line) or ('Mean' in line) or state == None:
            continue
        else:
            if state == 'mean':
                pixel_val = float(line.split()[0])
                curr_val.append(pixel_val)
            elif state == 'var':
                pixel_vals = [float(i) for i in line.split()]
                curr_val.append(pixel_vals)

    for i in range(len(imgs)):
        img = imgs[i]
        skio.imsave(os.path.join(args.output_dir, 'img%d.png' % i), img.astype(np.ubyte))
        np.save(os.path.join(args.output_dir, 'mean%d.npy' % i), img)
        np.save(os.path.join(args.output_dir, 'var%d.npy' % i), cov_mat[i])
    colors = ['r', 'g', 'b', 'y', 'm']


def parse_offline_sequence():
    imgs = []
    f = open(args.input_file, 'r')
    state, x, y, timestep = None, None, None, -1
    curr_val = {}
    re_com = re.compile('Component\[([0-9]+)\]')
    re_imx = re.compile('ImageX\[([0-9]+)\]')
    re_imy = re.compile('ImageY\[([0-9]+)\]')
    re_tim = re.compile('Time\[([0-9]+)\]')
    for line in f.readlines():
        contents = line.split()
        if 'query' in line:
            state = 'Query'
            if len(curr_val) > 0:
                curr_img = imgs[t]
                if (max([(curr_val[i], i) for i in curr_val])[1] == 'Component[2]'):
                    curr_img[y, x] = 1.0
                else:
                    curr_img[y, x] = 0.0
            x = int(re_imx.findall(line)[0])
            y = int(re_imy.findall(line)[0])
            t = int(re_tim.findall(line)[0])
            curr_val = {}
            if (t > timestep):
                imgs.append(np.zeros((args.ylen, args.xlen)))
                timestep = t
        elif 'loopend' in line:
            if len(curr_val) > 0:
                curr_img = imgs[t]
                if (max([(curr_val[i], i) for i in curr_val])[1] == 'Component[2]'):
                    curr_img[y, x] = 1.0
                else:
                    curr_img[y, x] = 0.0
            curr_val = {}
        elif state is None:
            continue
        else:
            curr_val[contents[0]] = float(contents[2])

    for i in range(len(imgs)):
        img = skimage.img_as_ubyte(imgs[i])
        skio.imsave(os.path.join(args.output_dir, 'img%d.png' % i), img)


def main():
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    queries = {'mean_var_offline': parse_mean_var_offline,
               'offline_sequence': parse_offline_sequence}
    if args.query_type in queries:
        queries[args.query_type]()
    else:
        print("Query %s not in set of supported queries" % args.query_type)

if __name__ == "__main__":
    main()
