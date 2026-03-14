"""
Process variation sampling with spatial correlation
"""

import numpy as np
from scipy.stats import multivariate_normal

def generate_correlated_samples(n_samples, correlation_matrix, sigma, random_state=None):
    """
    Generate spatially correlated process variation samples
    """
    n_vars = correlation_matrix.shape[0]
    
    cov_matrix = correlation_matrix * (sigma ** 2)
    
    samples = multivariate_normal.rvs(
        mean=np.zeros(n_vars),
        cov=cov_matrix,
        size=n_samples,
        random_state=random_state
    )
    
    if n_samples == 1:
        samples = samples.reshape(1, -1)
    
    return samples