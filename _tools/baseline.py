def baseline(timeseries, poly_ordr=2):
    '''estimation of dynamic baseline for input timeseries'''
    
    # poly_ordr  polynomial order for detrending
    # t_baseline:  timescale constant for baseline estimation (in seconds)
    # f_hipass:   highpass cutoff frequency
    # f_volume:    frequency of imaging a single stack (in Hz)
    
    # timeseries mean
    timeseries_mean = timeseries.mean()
    
    # length of interval of dynamic baseline time-scales
    ltau = (np.round(t_baseline * f_volume / 2) * 2 + 1).astype(int)
    
    # detrend with a low-order polynomial
    xtime = np.arange(timeseries.shape[0])
    coefpoly = np.polyfit(xtime, timeseries, poly_ordr)
    timeseries -= np.polyval(coefpoly, xtime)
    timeseries = np.concatenate((timeseries[::-1], timeseries, timeseries[::-1]))
    
    # highpass filter
    nyquist = f_volume / 2
    if (f_hipass > 1e-10) and (f_hipass < nyquist - 1e-10):
        f_rng = np.array([f_hipass, nyquist - 1e-10])
        krnl = signal.firwin(lt, f_rng / nyquist, pass_zero=False)
        timeseries = signal.filtfilt(krnl, 1, timeseries, padtype=None)
        
    # restore mean
    timeseries = timeseries - timeseries.mean() + timeseries_mean
    
    # compute dynamic baseline
    timeseries_df = pd.DataFrame(timeseries)
    baseline_df = timeseries_df.rolling(ltau, min_periods=1, center=True).quantile(0.1)
    baseline_df = baseline_df.rolling(ltau, min_periods=1, center=True).mean()
    baseline = np.ravel(baseline_df)
    baseline += np.percentile(timeseries - baseline, 1)
    assert(np.allclose(np.percentile(timeseries - baseline, 1), 0))
    
    return(timeseries[lt:2*lt], baseline[lt:2*lt])
