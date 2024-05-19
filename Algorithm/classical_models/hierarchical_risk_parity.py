# Code based on the method described in:
# "Advances in Financial Machine Learning", Marcos M. López de Prado , 2018
# Some improvements and tests based on:
# - MATHEMATICS AND PHYSICS ENGINEERING FINAL PROJECT, Hierarchical Risk Parity
#       portfolio optimization, by: Mikel Mercader Pérez
#       (https://upcommons.upc.edu/bitstream/handle/2117/350200/TFG.pdf)
# - Hierarchical Risk Parity - Implementation & Experiments (Part I)
#       (https://gmarti.gitlab.io/qfin/2018/10/02/hierarchical-risk-parity-part-1.html)


import denoising_correlation_matrix as dn
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import ClusterWarning, dendrogram, linkage
# from scipy.spatial.distance import pdist, squareform

from warnings import simplefilter
simplefilter("ignore", ClusterWarning)


def compute_hierarchical_tree_clustering(returns, method, draw_plots,
                                         denoise_method):
    if denoise_method == 0:
        corr = returns.corr()
    else:
        corr = dn.denoise(returns, denoise_method)

    if draw_plots:
        sns.heatmap(corr, cmap="coolwarm")

    distance_matrix = np.sqrt(0.5*(1-corr))

    # condensed_distance_matrix = pdist(distance_matrix)
    # Convert condensed distance matrix to squareform
    # square_distance_matrix = squareform(condensed_distance_matrix)

    linkage_matrix = linkage(distance_matrix, method)

    if draw_plots:
        Z = pd.DataFrame(linkage_matrix)
        plt.figure(figsize=(25, 10))
        dendrogram(Z, labels=np.array(returns.columns))
        plt.show()

    return linkage_matrix


def get_quasi_diagonalisation(linkage_matrix):
    linkage_matrix = linkage_matrix.astype(int)
    sort_ix = pd.Series([linkage_matrix[-1, 0], linkage_matrix[-1, 1]])
    num_items = linkage_matrix[-1, 3]

    while sort_ix.max() >= num_items:
        sort_ix.index = range(0, sort_ix.shape[0]*2, 2)
        df0 = sort_ix[sort_ix >= num_items]
        i = df0.index
        j = df0.values - num_items
        sort_ix[i] = linkage_matrix[j, 0]
        df0 = pd.Series(linkage_matrix[j, 1], index=i+1)
        sort_ix = pd.concat([sort_ix, df0])
        sort_ix = sort_ix.sort_index()
        sort_ix.index = range(sort_ix.shape[0])
    return sort_ix.tolist()


def get_cluster_var(cov, c_items):
    cov_ = cov.iloc[c_items, c_items]
    ivp = 1./np.diag(cov_)
    ivp /= ivp.sum()
    w_ = ivp.reshape(-1, 1)
    c_var = np.dot(np.dot(w_.T, cov_), w_)[0, 0]
    return c_var


def get_recursive_bisection(cov, sort_ix):
    weights = pd.Series(1.0, index=sort_ix)
    clustered_alphas = [sort_ix]

    while len(clustered_alphas) > 0:
        clustered_alphas = [i[int(j):int(k)] for i in clustered_alphas
                            for j, k in ((0, len(i)/2), (len(i)/2, len(i)))
                            if len(i) > 1]

        for i in range(0, len(clustered_alphas), 2):
            left_cluster = clustered_alphas[i]
            right_cluster = clustered_alphas[i+1]
            left_cluster_var = get_cluster_var(cov, left_cluster)
            right_cluster_var = get_cluster_var(cov, right_cluster)

            alloc_factor = float(1 - left_cluster_var /
                                 (left_cluster_var+right_cluster_var))
            weights[left_cluster] *= alloc_factor
            weights[right_cluster] *= 1-alloc_factor
    return weights


def compute_HRP_weights(returns, method="ward", draw_plots=False,
                        denoise_method=0):
    # Step 1 - Hierarchical Tree Clustering
    linkage_matrix = compute_hierarchical_tree_clustering(
        returns, method, draw_plots, denoise_method)

    # Step 2 - Quasi Diagonalisation
    sort_ix = get_quasi_diagonalisation(linkage_matrix)

    if draw_plots:
        stocks_compl = np.array(returns.columns)
        df_vis = returns[stocks_compl[sort_ix]]
        corr2 = df_vis.corr()
        sns.heatmap(corr2, cmap="coolwarm")

    # Step 3 - Recursive Bisection
    cov = returns.cov()
    weights_HRP = get_recursive_bisection(cov, sort_ix)
    new_index = [returns.columns[i] for i in weights_HRP.index]
    weights_HRP.index = new_index
    weights_HRP.name = "HRP"
    weights_HRP = weights_HRP.sort_index()
    return weights_HRP


# Other methods for comparison
def compute_minimum_variance_weights(returns):
    covariances = returns.cov()
    inv_covar = np.linalg.inv(covariances)
    u = np.ones(len(covariances))
    x = np.dot(inv_covar, u) / np.dot(u, np.dot(inv_covar, u))

    if x.min() < 0:  # Allows only positive weights
        pos_w = (x - x.min())
        x = pos_w / pos_w.sum()

    return pd.Series(x, index=returns.columns, name="MV")


def compute_risk_parity_weights(returns):
    covariances = returns.cov()
    weights = (1 / np.diag(covariances))
    x = weights / sum(weights)
    return pd.Series(x, index=returns.columns, name="RP")


def compute_unif_weights(returns):
    covariances = returns.cov()
    x = [1 / len(covariances) for i in range(len(covariances))]
    return pd.Series(x, index=returns.columns, name="unif")
