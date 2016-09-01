import argparse
import numpy as np
from scipy.misc import imread
from scipy.io import savemat, loadmat
import string
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(
    description="Compare predicted labels with ground truth labels.")
parser.add_argument('-p', '--predicted_mat',
                    help="Path to predicted mat made by labeled_image_to_mat.py")
parser.add_argument('-t', '--truth_mat',
                    help="Path of ground truth mat")
parser.add_argument('-g', '--graph',
                    help='Whether or not to save plots of statistics for each frame.',
                    default=False)
parser.add_argument('-o', '--output',
                    help='Where to save plot.')
args = parser.parse_args()

def compute_F1(num_true_pos, num_false_pos, num_false_neg):
    if num_true_pos == 0:
        return 0
    p_denom = float(num_true_pos + num_false_pos)
    r_denom = float(num_true_pos + num_false_neg)
    if p_denom == 0 or r_denom == 0:
        return -1
    p = float(num_true_pos)/p_denom 
    r = float(num_true_pos)/r_denom
    return 2.0 * p * r / (p + r)

def main():
    predicted_mat = loadmat(args.predicted_mat)['labels']
    truth_mat = loadmat(args.truth_mat)['labels']
    min_shape = np.minimum(predicted_mat.shape, truth_mat.shape)
    predicted = predicted_mat[:min_shape[0], :min_shape[1], :min_shape[2]]
    truth = truth_mat[:min_shape[0], :min_shape[1], :min_shape[2]]
        
    true_pos = np.logical_and(predicted, truth)
    false_pos = np.logical_and(predicted, np.logical_not(truth))
    false_neg = np.logical_and(np.logical_not(predicted), truth)
    
    total_true_pos = np.sum(true_pos)
    total_false_pos = np.sum(false_pos)
    total_false_neg = np.sum(false_neg)
    
    f1 = compute_F1(total_true_pos, total_false_pos, total_false_neg)
    
    frames_and_size = min_shape[0] * min_shape[1] * min_shape[2]
    avg_false_pos = float(total_false_pos) / float(frames_and_size)
    avg_false_neg = float(total_false_neg) / float(frames_and_size)
    
    if f1 < 0:
        print("Cannot compute statistics because ground truth has no positive results.")
    else:
        print("F1 Score: %f" % f1)
        if args.graph:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            scores = []
            for i in range(min_shape[2]):
                total_true_p = np.sum(true_pos[:, :, i])
                total_false_p = np.sum(false_pos[:, :, i])
                total_false_n = np.sum(false_neg[:, :, i])
                scores.append(compute_F1(total_true_p, total_false_p, total_false_n))
            x_axis = np.arange(0, len(scores))
            ax.scatter(x_axis, scores)
            #ax.set_xlim([0,len(x_axis)])
            #ax.set_ylim([0,1])
            plt.tight_layout()
            ax.set_xlim([0,len(x_axis) - 1])
            plt.savefig(args.output)

if __name__ == '__main__':
    main()
