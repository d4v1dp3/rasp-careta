import numpy as np
from scipy.signal import find_peaks

# 25 samples per second (in algorithm.h)
SAMPLE_FREQ = 50.0
# taking moving average of 4 samples when calculating HR
# in algorithm.h, "DONOT CHANGE" comment is attached
MA_SIZE = 2
# sampling frequency * 4 (in algorithm.h)
BUFFER_SIZE = 200

SMOOTHING_SIZE = 12


def calc_hr_and_spo2(ir_data, red_data):
    hr_valid = False
    hr = 0
    spo2 = 0
    spo2_valid = False

    heart_rate_span = [10, 250]  # max span of heart rate

    min_time_bw_samps = (60.0 / heart_rate_span[1])

    t_v = np.arange(0, BUFFER_SIZE / SAMPLE_FREQ, 1 / SAMPLE_FREQ).tolist()

    for i in range(len(red_data)):
        if red_data[i] < 90000.0:
            red_data[i] = 0

    for i in range(len(ir_data)):
        if ir_data[i] < 90000.0:
            ir_data[i] = 0

    Red_v = convolve_data(red_data)
    Ir_v = convolve_data(ir_data)

    red_locmax, a = find_peaks(Red_v, distance=10, prominence=[100, 3500], width=[10, 50])
    red_locmin, b = find_peaks(Red_v * -1, distance=10, prominence=[100, 3500], width=[10, 50])
    ir_locmax, c = find_peaks(Ir_v, distance=10, prominence=[100, 3500], width=[10, 50])
    ir_locmin, d = find_peaks(Ir_v * -1, distance=10, prominence=[100, 3500], width=[10, 50])

    #print("LEN:{0},{1} - {2},{3}".format(len(red_locmax), len(red_locmin), len(ir_locmax), len(ir_locmin) ))

    if len(red_locmax) < 2 or len(ir_locmax) < 2 or len(red_locmin) < 2 or len(ir_locmin) < 2:
        return hr, hr_valid, spo2, spo2_valid

    t_peaks = [t_v[kk] for kk in red_locmax]
    hr = 60.0 / np.mean(np.diff(t_peaks))
    hr_valid = True

    red_ac = 0
    ir_ac = 0

    red_dc = 0
    ir_dc = 0

    idx = 0
    if red_locmax[0] < red_locmin[0]:
        idx = 1

    for i in range(1, min(len(red_locmax), len(red_locmin)) - idx):
        if Red_v[red_locmax[i]] - Red_v[red_locmin[i + idx]] > red_ac and red_locmax[i] - red_locmin[i + idx] < 20 and red_locmin[i + idx - 1] - red_locmin[i + idx] < 35:
            red_ac = Red_v[red_locmax[i]] - Red_v[red_locmin[i + idx]]
            red_dc = Red_v[red_locmin[i + idx - 1]] + (Red_v[red_locmin[i + idx - 1]] - Red_v[red_locmin[i + idx]]) * 0.85

    idx = 0
    if ir_locmax[0] < ir_locmax[0]:
        idx = 1

    for i in range(1, min(len(ir_locmax), len(ir_locmin)) - idx):
        if Ir_v[ir_locmax[i]] - Ir_v[ir_locmin[i + idx]] > ir_ac and ir_locmax[i] - ir_locmin[i + idx] < 20  and ir_locmin[i + idx - 1] - ir_locmin[i + idx] < 35:
            ir_ac = Ir_v[ir_locmax[i]] - Ir_v[ir_locmin[i + idx]]
            ir_dc = Ir_v[ir_locmin[i + idx - 1]] + (Ir_v[ir_locmin[i + idx - 1]] - Ir_v[ir_locmax[i + idx]]) * 0.85

    num = red_ac * ir_dc
    den = ir_ac * red_dc

    if den != 0:
        r = num / den
        spo2_valid = True
        spo2 = 104 - 17 * r
    # spo2 = (-45.060) * (r ** 2) + (30.054) * r + 94.845

    return hr, hr_valid, spo2, spo2_valid


def convolve_data(data):
    data_v = np.convolve(data, np.ones((SMOOTHING_SIZE,)), 'same') / SMOOTHING_SIZE
    data_v = np.append(np.repeat(data_v[int(SMOOTHING_SIZE / 2)], int(SMOOTHING_SIZE / 2)), data_v[int(SMOOTHING_SIZE / 2):-int(SMOOTHING_SIZE / 2)])
    data_v = np.append(data_v, np.repeat(data_v[-int(SMOOTHING_SIZE / 2)], int(SMOOTHING_SIZE / 2)))
    return data_v
