import numpy as np
import matplotlib.pyplot as plt

ST =  4
FS = 25
MAX_HR = 180
MIN_HR = 40
BUFFER_SIZE = FS*ST
FS60 = FS*60
LOWEST_PERIOD = FS60/MAX_HR
HIGHEST_PERIOD = FS60/MIN_HR

min_autocorrelation_ratio = 0.5
min_pearson_correlation = 0.8

sum_X2 = 83325
mean_X = float(BUFFER_SIZE-1)/2.0
smoothing_size = 6  # convolution smoothing size
n_last_peak_interval = LOWEST_PERIOD

def calc_hr_and_spo2(ir_data, red_data):
    global n_last_peak_interval

    #for i in range(len(ir_data)):
    #    if ir_data[i] < 90000.0:
    #        ir_data[i] = 0

    #for i in range(len(red_data)):
    #    if red_data[i] < 90000.0:
    #        red_data[i] = 0

    #red_data = np.convolve(red_data, np.ones((smoothing_size,)), 'same') / smoothing_size
    #red_data = np.append(np.repeat(red_data[int(smoothing_size / 2)], int(smoothing_size / 2)), red_data[int(smoothing_size / 2):-int(smoothing_size / 2)])
    #red_data = np.append(red_data, np.repeat(red_data[-int(smoothing_size / 2)], int(smoothing_size / 2)))

    #ir_data = np.convolve(ir_data, np.ones((smoothing_size,)), 'same') / smoothing_size
    #ir_data = np.append(np.repeat(ir_data[int(smoothing_size / 2)], int(smoothing_size / 2)),ir_data[int(smoothing_size / 2):-int(smoothing_size / 2)])
    #ir_data = np.append(ir_data, np.repeat(ir_data[-int(smoothing_size / 2)], int(smoothing_size / 2)))

    ratio = 0.0
    correl = 0.0

    buffer_size = len(ir_data)

    xdata = range(buffer_size)
    # plt.plot(xdata, pun_ir_buffer)
    # plt.plot(xdata, pun_red_buffer)

    f_ir_mean = np.mean(ir_data)
    f_red_mean = np.mean(red_data)

    an_x = ir_data - f_ir_mean
    an_y = red_data - f_red_mean

    beta_ir = linear_regression_beta(an_x, mean_X, sum_X2)
    beta_red = linear_regression_beta(an_y, mean_X, sum_X2)

    x = -mean_X
    for k in range(buffer_size):
        an_x[k] -= beta_ir * x
        an_y[k] -= beta_red * x
        x += 1

    #plt.plot(xdata, pun_ir_buffer)
    #plt.plot(xdata, pun_red_buffer)

    [f_y_ac, f_red_sumsq] = rms(an_y)
    [f_x_ac, f_ir_sumsq] = rms(an_x)

    correl = Pcorrelation(an_x, an_y) / np.sqrt(f_red_sumsq * f_ir_sumsq)

    #plt.show()

    if correl >= min_pearson_correlation:
        if LOWEST_PERIOD == n_last_peak_interval:
            n_last_peak_interval = initialize_periodicity_search(an_x, n_last_peak_interval, HIGHEST_PERIOD, min_autocorrelation_ratio, f_ir_sumsq)
        if n_last_peak_interval != 0:
            [n_last_peak_interval, ratio] = signal_periodicity(an_x, n_last_peak_interval, LOWEST_PERIOD, HIGHEST_PERIOD, min_autocorrelation_ratio, f_ir_sumsq)
    else:
        n_last_peak_interval = 0

    if n_last_peak_interval != 0:
        pn_heart_rate = int(FS60 / n_last_peak_interval)
        pch_hr_valid = True
    else:
        n_last_peak_interval = LOWEST_PERIOD
        pn_heart_rate = -999
        pch_hr_valid = False
        pn_spo2 = -999
        pch_spo2_valid = False
        return [pn_spo2, pch_spo2_valid, pn_heart_rate, pch_hr_valid]

    xy_ratio = (f_y_ac * f_ir_mean) / (f_x_ac * f_red_mean)
    if 0.02 < xy_ratio < 1.84:
        pn_spo2 = (-45.060 * xy_ratio + 30.354) * xy_ratio + 94.845
        pch_spo2_valid = True
    else:
        pn_spo2 = -999
        pch_spo2_valid = False

    return [pn_spo2, pch_spo2_valid, pn_heart_rate, pch_hr_valid]

def linear_regression_beta(pn_x, xmean, sum_x2):
    beta = 0.0
    i = 0
    x = -xmean
    while x <= xmean:
        beta += x * pn_x[i]
        i += 1
        x += 1
    return beta / sum_x2

def autocorrelation(pn_x, n_lag):
    n_temp = len(pn_x) - n_lag
    sum = 0.0
    if n_temp <= 0:
        return sum
    for i in range(n_temp):
        sum += pn_x[i] * pn_x[i + n_lag]
    return sum / n_temp

def initialize_periodicity_search(pn_x, p_last_periodicity, n_max_distance, min_aut_ratio, aut_lag0):
    n_lag = 0
    aut, aut_right = 0.0, 0.0
    # At this point, *p_last_periodicity = LOWEST_PERIOD. Start walking to the right,
    # two steps at a time, until lag ratio fulfills quality criteria or HIGHEST_PERIOD
    # is reached.
    n_lag = p_last_periodicity
    aut_right = aut = autocorrelation(pn_x, n_lag)
    # Check sanity
    if aut / aut_lag0 >= min_aut_ratio:
        # Either quality criterion, min_aut_ratio, is too low, or heart rate is too high.
        # Are we on autocorrelation's downward slope? If yes, continue to a local minimum.
        # If not, continue to the next block.
        repeat = True
        while repeat:
            aut=aut_right
            n_lag += 2
            aut_right = autocorrelation(pn_x, n_lag)
            repeat = aut_right / aut_lag0 >= min_aut_ratio and aut_right < aut and n_lag <= n_max_distance

        if n_lag > n_max_distance:
            # This should never happen, but if does return failure
            p_last_periodicity=0
            return [p_last_periodicity]

        aut = aut_right

    # Walk to the right.
    repeat = True
    while repeat:
        aut = aut_right
        n_lag += 2
        aut_right = autocorrelation(pn_x, n_lag)
        repeat = aut_right / aut_lag0 < min_aut_ratio and n_lag <= n_max_distance

    if n_lag > n_max_distance:
        # This should never happen, but if does return failure
        p_last_periodicity=0
    else:
        p_last_periodicity = n_lag
    return p_last_periodicity

def signal_periodicity(pn_x, p_last_periodicity, n_min_distance, n_max_distance, min_aut_ratio, aut_lag0):
    left_limit_reached = False

    n_lag = p_last_periodicity
    aut_save = aut = autocorrelation(pn_x, n_lag)

    aut_left = aut
    repeat = True
    while repeat:
        aut = aut_left
        n_lag -= 1
        aut_left = autocorrelation(pn_x, n_lag)
        repeat = aut_left > aut and n_lag >= n_min_distance

    if n_lag < n_min_distance:
        left_limit_reached = True
        n_lag = p_last_periodicity
        aut=aut_save
    else:
        n_lag += 1

    if n_lag == p_last_periodicity:
        aut_right=aut
        repeat = True
        while repeat:
            aut=aut_right
            n_lag += 1
            aut_right = autocorrelation(pn_x, n_lag)
            repeat = aut_right > aut and n_lag <= n_max_distance

        if n_lag > n_max_distance:
            n_lag = 0 # Indicates failure
        else:
            n_lag -= 1
        if n_lag == p_last_periodicity and left_limit_reached:
            n_lag = 0 # Indicates failure

    ratio = aut / aut_lag0
    if ratio < min_aut_ratio:
        n_lag = 0 # Indicates failure
    p_last_periodicity = n_lag
    return [p_last_periodicity, ratio]

def rms(pn_x):
    sumsqr = np.mean(pn_x**2)
    rms = np.sqrt(sumsqr)
    return [rms, sumsqr]

def Pcorrelation(pn_x, pn_y):
    r = 0
    size = len(pn_x)
    for x in range(size):
        r += pn_x[x]*pn_y[x]
    r /= size
    return r
