import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

if __name__ == '__main__':
    filename = '/Users/thomasusherwood/lab_code/elliott_lab/PDD_project/' + \
               'IR-RED-AIF/data/ICG02_PIG006_Volts_20201111_125109.xls'
    fid = open(filename, "r")
    X1 = np.loadtxt(fid, skiprows=6)
    fid.close()

    fs = 500  # sampling rate
    tbl = [10, 60]  # reliable baseline data

    # red and ir channels (raw)
    RED = X1[:, 4].T
    IR = X1[:, 5].T

    RED_base = np.array(RED[1000:41000])  # np.array(RED[999:41000])
    print(RED_base.shape)
    IR_base = np.array(IR[1000:41000])  # np.array(IR[999:41000])
    print(IR_base.shape)
    welch_base = np.vstack((RED_base, IR_base))

    # powerspectrum
    # f, P = signal.welch(welch_base, fs=fs, nperseg=71, nfft=256)
    f, P = signal.welch(welch_base, fs=fs,
                        nperseg=10000)  # nperseg and nfft should be the same, make noverlap end with end of data
    print(f'f shape: {f.shape}')
    print(f'P shape: {P.shape}')
    print(f'f start: {f[0]}\nf end: {f[-1]}\n')

    bpm = f * 60

    # get heart-rate
    plt.figure('bpm vs P')
    # plt.plot(bpm, P)
    plt.plot(bpm.T, P[0, :])
    plt.plot(bpm.T, P[1, :])
    plt.title('select the center of the heart-rate peak')
    plt.xlim(12, 180)
    plt.ylim(0, 0.00005)
    plt.xlabel('frequency (beats per min).')
    ghr = plt.ginput(n=1, timeout=0, show_clicks=True)[0][0]
    fhr = ghr / 60
    plt.close('bpm vs P')
