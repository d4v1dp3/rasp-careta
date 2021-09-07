
import numpy as np
from scipy.signal import butter, lfilter

Fs = 10
L = 200
nyq = Fs / 2.0

def butter_lowpass_filter(data, cutoff, fs, order):
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y

def frequency_breath(flow_data):
    f = Fs*np.linspace(0, (L/2)-1, L/2)/float(L)

    filter_y = butter_lowpass_filter(flow_data, 3, Fs, 3)

    Y = np.fft.fft(filter_y)

    P2 = np.abs(Y/L)
    P1 = P2[0:L/2]

    index = np.argmax(P1)

    if index > 30:
        index = 0
    #else:
    #    index = index + 1

    frec = f[index]

    return frec * 60
