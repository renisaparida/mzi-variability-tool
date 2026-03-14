"""
Yield calculation and statistical analysis
"""

import pandas as pd
import numpy as np

def analyze_yield(all_metrics, specs, verbose=True):
    """
    Calculate yield and statistical metrics
    """
    df = pd.DataFrame(all_metrics)
    
    yield_ER = 100 * df['pass_ER'].sum() / len(df)
    yield_IL = 100 * df['pass_IL'].sum() / len(df)
    yield_overall = 100 * df['pass_overall'].sum() / len(df)
    
    ER_mean = df['ER_out1'].mean()
    ER_std = df['ER_out1'].std()
    ER_min = df['ER_out1'].min()
    ER_max = df['ER_out1'].max()
    
    IL_mean = df['IL_out1'].mean()
    IL_std = df['IL_out1'].std()
    IL_min = df['IL_out1'].min()
    IL_max = df['IL_out1'].max()
    
    wavelength_shift_mean = (df['lambda_peak_out1'].mean() - 1550e-9) * 1e9
    wavelength_shift_std = df['lambda_peak_out1'].std() * 1e9
    
    Cpk_ER = (ER_mean - specs['target_ER']) / (3 * ER_std) if ER_std > 0 else 0
    Cpk_IL = (specs['target_IL'] - IL_mean) / (3 * IL_std) if IL_std > 0 else 0
    
    yield_stats = {
        'yield_ER': yield_ER,
        'yield_IL': yield_IL,
        'yield_overall': yield_overall,
        'ER_mean': ER_mean,
        'ER_std': ER_std,
        'ER_min': ER_min,
        'ER_max': ER_max,
        'IL_mean': IL_mean,
        'IL_std': IL_std,
        'IL_min': IL_min,
        'IL_max': IL_max,
        'wavelength_shift_mean_nm': wavelength_shift_mean,
        'wavelength_shift_std_nm': wavelength_shift_std,
        'Cpk_ER': Cpk_ER,
        'Cpk_IL': Cpk_IL,
    }
    
    if verbose:
        print("\n" + "="*60)
        print("YIELD ANALYSIS RESULTS")
        print("="*60)
        print(f"\nTarget Specifications:")
        print(f"  Extinction Ratio: > {specs['target_ER']} dB")
        print(f"  Insertion Loss:   < {specs['target_IL']} dB")
        
        print(f"\nYield:")
        print(f"  ER > {specs['target_ER']}dB:     {yield_ER:6.2f}%")
        print(f"  IL < {specs['target_IL']}dB:      {yield_IL:6.2f}%")
        print(f"  Overall:          {yield_overall:6.2f}%")
        
        print(f"\nExtinction Ratio Statistics:")
        print(f"  Mean:   {ER_mean:6.2f} dB")
        print(f"  Std:    {ER_std:6.2f} dB")
        print(f"  Min:    {ER_min:6.2f} dB")
        print(f"  Max:    {ER_max:6.2f} dB")
        print(f"  Cpk:    {Cpk_ER:6.2f}")
        
        print(f"\nInsertion Loss Statistics:")
        print(f"  Mean:   {IL_mean:6.2f} dB")
        print(f"  Std:    {IL_std:6.2f} dB")
        print(f"  Min:    {IL_min:6.2f} dB")
        print(f"  Max:    {IL_max:6.2f} dB")
        print(f"  Cpk:    {Cpk_IL:6.2f}")
        
        print(f"\nWavelength Shift:")
        print(f"  Mean:   {wavelength_shift_mean:6.2f} nm")
        print(f"  Std:    {wavelength_shift_std:6.2f} nm")
        
        print("="*60 + "\n")
    
    return df, yield_stats