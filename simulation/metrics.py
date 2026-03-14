"""
Performance metrics extraction
"""

import numpy as np

def extract_metrics(wavelengths, P_out1, P_out2):
    """
    Extract key performance indicators from MZI response
    """
    epsilon = 1e-12

    ER_out1 = 10 * np.log10((np.max(P_out1) + epsilon) / (np.min(P_out1) + epsilon))
    ER_out2 = 10 * np.log10((np.max(P_out2) + epsilon) / (np.min(P_out2) + epsilon))

    IL_out1 = -10 * np.log10(np.max(P_out1) + epsilon)
    IL_out2 = -10 * np.log10(np.max(P_out2) + epsilon)

    # Track the peak nearest to 1550nm rather than the global max.
    # With FSR~4nm there are ~10 peaks in the 1530-1570nm window; using argmax
    # causes the tracker to jump between FSR orders across MC samples, giving
    # a spuriously large wavelength-shift std (~11nm instead of ~2nm).
    target_lam = 1550e-9

    peaks1 = [i for i in range(1, len(P_out1)-1)
               if P_out1[i] >= P_out1[i-1] and P_out1[i] >= P_out1[i+1]]
    if peaks1:
        nearest1 = min(peaks1, key=lambda i: abs(wavelengths[i] - target_lam))
        lambda_peak_out1 = wavelengths[nearest1]
    else:
        lambda_peak_out1 = wavelengths[np.argmax(P_out1)]

    peaks2 = [i for i in range(1, len(P_out2)-1)
               if P_out2[i] >= P_out2[i-1] and P_out2[i] >= P_out2[i+1]]
    if peaks2:
        nearest2 = min(peaks2, key=lambda i: abs(wavelengths[i] - target_lam))
        lambda_peak_out2 = wavelengths[nearest2]
    else:
        lambda_peak_out2 = wavelengths[np.argmax(P_out2)]

    max_P1 = np.max(P_out1)
    half_max = max_P1 / 2
    above_half = P_out1 > half_max

    if np.any(above_half):
        indices = np.where(above_half)[0]
        bandwidth_out1 = wavelengths[indices[-1]] - wavelengths[indices[0]]
    else:
        bandwidth_out1 = 0

    total_power = np.mean(P_out1 + P_out2)
    uniformity = 1 - abs(np.mean(P_out1) - np.mean(P_out2)) / (total_power + epsilon)

    return {
        'ER_out1': ER_out1,
        'ER_out2': ER_out2,
        'IL_out1': IL_out1,
        'IL_out2': IL_out2,
        'lambda_peak_out1': lambda_peak_out1,
        'lambda_peak_out2': lambda_peak_out2,
        'bandwidth_out1': bandwidth_out1,
        'uniformity': uniformity,
    }