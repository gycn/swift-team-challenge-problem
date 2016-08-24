import argparse
import numpy as np
import os
import skimage.io as skio

parser = argparse.ArgumentParser(
    description="Convert means/variances to text versions")
parser.add_argument('--input_dir',
    help="Directory containing means and variances to convert")
parser.add_argument('--data_dir',
    help="Directory containing image data")
parser.add_argument('--num_timesteps',
    help="Number of timesteps to compute tight mean/covariance")
parser.add_argument('--query_type',
    help="Query type")
args = parser.parse_args()

def save_img_txt():
    data = []
    for img_path in sorted(os.listdir(args.data_dir)):
        img = skio.imread(os.path.join(args.data_dir, img_path))
        if len(img.shape) < 3:
            img = np.dstack((img, img, img))
        data.append(img)
    data = np.array(data)
    t, ylen, xlen, c = data.shape
    colors = ['r', 'g', 'b']
    for channel in range(c):
        data_slice = data[:, :, :, channel].reshape((t, ylen*xlen))
        np.savetxt(
            os.path.join(args.input_dir,
                         'data_{}.txt'.format(colors[channel])), data_slice)


def get_tight_mean_var():
    data = []
    for img_path in sorted(os.listdir(args.data_dir)):
        img = skio.imread(os.path.join(args.data_dir, img_path)) 
        if len(img.shape) < 3:
            img = np.dstack((img, img, img))
        data.append(img)
    data = np.array(data)
    t, ylen, xlen, c = data.shape
    small_mean = np.mean(data, axis=0)
    norm_data = data - small_mean
    small_mean = np.zeros((ylen, xlen, c))
    small_var = np.zeros((ylen, xlen, c, c))
    for x in range(xlen):
        print(x)
        for y in range(ylen):
            H, edges = np.histogramdd(data[:, y, x], bins=(24,) * 3,
                                      range=((0, 255), (0, 255), (0, 255)))
            bin_idx = np.unravel_index(np.argmax(H), H.shape)
            mean = np.array([(edges[i][bin_idx[i]] + edges[i][bin_idx[i] + 1]) \
                              / 2 for i in range(len(edges))])
            small_mean[y, x] = mean

            cov = norm_data[:, y, x].T.dot(norm_data[:, y, x]) / (t - 1)
            if np.linalg.det(cov) < 1e-2:
                cov = np.eye(3)
            small_var[y, x] = cov
    return small_mean.reshape(xlen * ylen, c), small_var.flatten()


def read_local_params():
    i = 0
    mean_arr, var_arr = [], []
    while True:
        mean_file = os.path.join(args.input_dir, 'mean%d.npy' % i)
        var_file = os.path.join(args.input_dir, 'var%d.npy' % i)
        if not os.path.exists(mean_file):
            break
        mean, var = np.load(mean_file), np.load(var_file)
        mean_arr.append(mean.reshape(mean.shape[0] * mean.shape[1], mean.shape[2]))
        var_arr.append(var.flatten())
        i += 1
    return mean_arr, var_arr


def main():
    mean_arr, var_arr = read_local_params()
    if args.query_type == 'read_img_sequence':
        small_mean, small_var = get_tight_mean_var()
        mean_arr.append(small_mean)
        var_arr.append(small_var)
        save_img_txt()
    np.savetxt(os.path.join(args.input_dir, "means.txt"),
               np.vstack(mean_arr))
    np.savetxt(os.path.join(args.input_dir, "vars.txt"),
               np.vstack(var_arr))

if __name__ == "__main__":
    main()
