import numpy as np

DESIGN = {
    'waveguide_width': 490e-9,
    'waveguide_height': 220e-9,
    'coupler_gap': 200e-9,
    'arm_length_diff': 150e-6,
    'wavelength_range': (1530e-9, 1570e-9),
    'wavelength_points': 100,
}

SPECS = {
    'target_ER': 30,
    'target_IL': 1.0,
}

VARIATIONS = {
    'width_sigma': 12e-9,
    'height_sigma': 8e-9,
    'gap_sigma': 4e-9,
    'length_sigma': 40e-9,
    'correlation_length': 100e-6,
}

CORRELATION_MATRIX = np.array([
    [1.0,  0.9,  0.3,  0.3],
    [0.9,  1.0,  0.3,  0.3],
    [0.3,  0.3,  1.0,  0.5],
    [0.3,  0.3,  0.5,  1.0]
])

MONTE_CARLO = {
    'n_samples': 5000,
    'random_seed': 999,
    'parallel': False,
}

OPTIMIZATION = {
    'width_offset_bounds': (-15e-9, 5e-9),
    'length_offset_bounds': (-100e-9, 200e-9),
    'maxiter': 15,
    'popsize': 8,
    'quick_eval_samples': 1000,
}

OUTPUT = {
    'output_dir': 'outputs',
    'save_plots': True,
    'save_csv': True,
    'dpi': 300,
}