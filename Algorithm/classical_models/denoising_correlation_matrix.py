# Code based on the methods described in:
# "Machine Learning for Asset Managers", Marcos M. López de Prado , 2020
# Some improvements and tests based on:
# - janestreet-denoising-RMT, FERNANDO RAMACCIOTTI
#       (https://www.kaggle.com/code/fernandoramacciotti/janestreet-denoising-rmt/notebook)


import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.neighbors import KernelDensity


def mpPDF(var, q, pts):
    # Marcenko-Pastur pdf
    # q=T/N
    eMin, eMax = var*(1-(1./q)**.5)**2, var*(1+(1./q)**.5)**2
    eVal = np.linspace(eMin, eMax, pts)
    pdf = q/(2*np.pi*var*eVal)*((eMax-eVal)*(eVal-eMin))**.5
    pdf = pd.Series(pdf.reshape(-1,), index=eVal.reshape(-1,))
    return pdf


def getPCA(matrix):
    # Get eVal,eVec from a Hermitian matrix
    eVal, eVec = np.linalg.eigh(matrix)
    indices = eVal.argsort()[::-1]  # arguments for sorting eVal desc
    eVal, eVec = eVal[indices], eVec[:, indices]
    eVal = np.diagflat(eVal)
    return eVal, eVec


def fitKDE(obs, bWidth, kernel='gaussian', x=None):
    # Fit kernel to a series of obs, and derive the prob of obs
    # x is the array of values on which the fit KDE will be evaluated
    if len(obs.shape) == 1:
        obs = obs.reshape(-1, 1)
    kde = KernelDensity(kernel=kernel, bandwidth=bWidth).fit(obs)
    if x is None:
        x = np.unique(obs).reshape(-1,)
    if len(x.shape) == 1:
        x = x.reshape(-1, 1)
    logProb = kde.score_samples(x)  # log(density)
    pdf = pd.Series(np.exp(logProb), index=x.flatten())
    return pdf


def cov2corr(cov):
    # Derive the correlation matrix from a covariance matrix
    std = np.sqrt(np.diag(cov))
    corr = cov/np.outer(std, std)
    corr[corr < -1], corr[corr > 1] = -1, 1  # numerical error
    return corr


def errPDFs(var, eVal, q, bWidth, pts=1000):
    # Fit error
    pdf0 = mpPDF(var, q, pts)  # theoretical pdf
    pdf1 = fitKDE(eVal, bWidth, x=pdf0.index.values)  # empirical pdf
    sse = np.sum((pdf1-pdf0)**2)
    return sse


def findMaxEval(eVal, q, bWidth):
    # Find max random eVal by fitting Marcenko’s dist
    out = minimize(lambda *x: errPDFs(*x), .5, args=(eVal, q, bWidth),
                   bounds=((1E-5, 1-1E-5),))
    if out['success']:
        var = out['x'][0]
    else:
        var = 1
    eMax = var*(1+(1./q)**.5)**2
    return eMax, var


def denoisedCorr(eVal, eVec, nFacts):
    # Remove noise from corr by fixing random eigenvalues
    eVal_ = np.diag(eVal).copy()
    eVal_[nFacts:] = eVal_[nFacts:].sum()/float(eVal_.shape[0] - nFacts)
    eVal_ = np.diag(eVal_)
    corr1 = np.dot(eVec, eVal_).dot(eVec.T)
    corr1 = cov2corr(corr1)
    return corr1


def denoisedCorr2(eVal, eVec, nFacts, alpha):
    # Remove noise from corr through targeted shrinkage
    eValL, eVecL = eVal[:nFacts, :nFacts], eVec[:, :nFacts]
    eValR, eVecR = eVal[nFacts:, nFacts:], eVec[:, nFacts:]
    corr0 = np.dot(eVecL, eValL).dot(eVecL.T)
    corr1 = np.dot(eVecR, eValR).dot(eVecR.T)
    corr2 = corr0+alpha*corr1+(1-alpha)*np.diag(np.diag(corr1))
    return corr2


def denoise(returns, method, bWidth=0.01, alpha=0.5):
    q = returns.shape[0] / returns.shape[1]
    cov = returns.cov().values
    corr0 = cov2corr(cov)

    eVal0, eVec0 = getPCA(corr0)
    eMax0, _ = findMaxEval(np.diag(eVal0), q, bWidth)
    nFacts0 = eVal0.shape[0] - np.diag(eVal0)[::-1].searchsorted(eMax0)
    if method == 1:
        corr_denoised = denoisedCorr(eVal0, eVec0, nFacts0)
    else:
        corr_denoised = denoisedCorr2(eVal0, eVec0, nFacts0, alpha)

    corr_denoised = np.round(corr_denoised, 6)
    return corr_denoised
