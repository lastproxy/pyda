"""Data Assimilation Effectiveness Quantification

Module of functions to evaluate the effectiveness of Data Assimilation
methods. Mainly the evaluation of effectiveness is done by computing the
KL-divergence between the analysis ensemble and the background ensemble along
with the data likelihood under the analysis ensemble. This can be done
explicitly for the Kalman Filter schemes which assume Gaussianity. For the
sequential Monte Carlo and Particle Filter methods we use Kernel Density
Approximation of the distributions.

"""

import numpy as np 
import math

# First we compute the Kullback-Leibler Divergence for two Gaussian
# distributions. We will need to pass the ensemble and analysis
# measurement distributions to do this. The mean and covariance are
# then formed from these. An alternative would be to pass the mean and
# covariance matrices.
#      <Ensemble Observation Arrays> = (measurement size)x(ensemble size)
def ensemble_KLdiv(ensemble_observations, analysis_observations):
    # Collect data sizes
    EnSize = ensemble_observations.shape[1]
    MeaSize = ensemble_observations.shape[0]

    # Calculate analysis and ensemble means
    Emean = (1./float(EnSize))*ensemble_observations.sum(1)
    Amean = (1./float(EnSize))*analysis_observations.sum(1)

    # Compute covariance matrices
    dE = ensemble_observations - np.tile(Emean.reshape(MeaSize,1),(1,EnSize))
    dA = analysis_observations - np.tile(Amean.reshape(MeaSize,1),(1,EnSize))

    Ecov = (1./float(EnSize-1))*np.dot(dE,dE.transpose())
    Acov = (1./float(EnSize-1))*np.dot(dA,dA.transpose())

    # Now compute D_{KL}(analysis | ensemble) for the Gaussians.
    # We compute this in three parts
    KL1 = np.trace(np.linalg.solve(Ecov,Acov))
    KL2 = np.dot((Amean - Emean),np.linalg.solve(Ecov,(Amean - Emean)))
    KL3 = np.linalg.det(Acov)/np.linalg.det(Ecov)
    KLdiv = 0.5*(KL1 + KL2 - math.log(KL3) - MeaSize)

    return KLdiv

# We return the likelihood of a data point given an analysis ensemble
# of observations. The analysis observation ensemble is used to
# compute an estimated mean and covariance. A Gaussian density with
# this mean and covariance is then evaluated at the data point to
# return the likelihood.
def GuassLikelihood(data, analysis_observations):
    # Collect data sizes
    EnSize = analysis_observations.shape[1]
    MeaSize = analysis_observations.shape[0]

    # Calculate analysis mean
    Amean = (1./float(EnSize))*analysis_observations.sum(1)

    # Compute covariance matrix
    dA = analysis_observations - np.tile(Amean.reshape(MeaSize,1),(1,EnSize))
    Acov = (1./float(EnSize-1))*np.dot(dA,dA.transpose())

    # Compute Gaussian likelihood
    Coef = math.sqrt(math.pow((2*math.pi),MeaSize)*np.linalg.det(Acov))

    Arg = 0.5*(np.dot((data - Amean),np.linalg.solve(Acov,(data - Amean))))

    GaussLikelihood = math.exp(-Arg)/Coef

    return GaussLikelihood

# We return the Mahalonobis Distance between a set of observations
# and the mean of an ensemble/analysis. The distance is scaled by the 
# covariance of the ensemble. 
# If the data is m and the ensemble mean is mu with covariance C then
# the Mahalonobis distance is given by
#     d(m,mu) = (m - mu)^T inv(C) (m - mu)
def Mdist(data, Amean, ACov):
    D = math.sqrt(np.dot((data - Amean),np.linalg.solve(ACov,(data - Amean))))
    
    return D
