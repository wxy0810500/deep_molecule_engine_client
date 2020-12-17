# all proteins are checked that rec.pdbqt contains only lines startswith ATOM
# this script will be incorrect if above condition is not satisfied
# check 'check_pocket.ipynb' for details

import os
import os.path as osp

import numpy as np


def distance_matrix(pts1, pts2):
    # pts.shape = k, 3
    sumsq1 = (pts1 ** 2).sum(axis=1)
    sumsq2 = (pts2 ** 2).sum(axis=1)
    k2 = pts2.shape[0]
    dis_cor = sumsq1 + sumsq2.reshape(k2, 1) - 2 * pts2.dot(pts1.T)
    return dis_cor[0]


def run(file, cxyz, cutoff_r=15):
    savedir = './pocket_r' + str(cutoff_r)
    if not osp.exists(savedir):
        os.makedirs(savedir)

    p = './' + file
    if not '.pdb' in p:
        print('ERROR!')
        return

    with open(p, 'r') as fp:
        lns = fp.readlines()

    xyz = []
    valid_lns = []
    for ln in lns:
        if ln.startswith('ATOM'):
            x = float(ln[30:38])
            y = float(ln[38:46])
            z = float(ln[46:54])
            xyz.append([x, y, z])
            valid_lns.append(ln)
    xyz = np.array(xyz)

    cxyz = np.array(cxyz).reshape(1, 3)

    d = distance_matrix(xyz, cxyz)
    pocket_idx = np.where(d < (cutoff_r ** 2))[0]
    pocket = [valid_lns[i] for i in pocket_idx]

    with open(osp.join(savedir, file.split('.')[0] + '_pocket_r15.pdb'), 'w') as fp:
        fp.writelines(pocket)


if __name__ == '__main__':
    cxyz = (262.916, 229.773, 196.784)
    file = ['7cm7.pdb']
    for f in file:
        run(f, cxyz)
