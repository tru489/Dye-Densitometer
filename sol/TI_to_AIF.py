#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 22:59:55 2020

@author: thomasusherwood
"""

import numpy as np
from pandas import read_csv
from scipy import interpolate, signal
import matplotlib.pyplot as plt
from getextinctioncoef import getextinctioncoef
from remezord import remezord
from typing import List


def TI_to_AIF(filename: str,
              wv: List[float] = [805, 940],
              inv: bool = False,
              filt_method: str = 'upenn',
              savedata: int = 0) -> tuple:
    """

    :param filename: name of file to save AIF to
    :param wv:
    :param inv: switches raw red and IR channels
    :param filt_method: method for FIR filter to be applied to data
    :param savedata: specifies whether to save data
    :return:
    """
    # open the Texas Instruments Volts output.
    X1 = np.array(read_csv(filename, header=2))
    sao2_thb = np.array(read_csv(filename,usecols=[0],nrows=2,header=None))
    if sao2_thb[0] == 0 and sao2_thb[1] == 0:
        SaO2 = 0.98
        tHb = 14
    else:
        SaO2 = sao2_thb[0]
        tHb = sao2_thb[1]
    # fid = open(filename, "r")
    # X1 = np.loadtxt(fid, skiprows=6)
    # fid.close()
    # SaO2 = 0.98
    # tHb = 14

    fs = 500  # sampling rate
    tbl = [10, 60]  # reliable baseline data

    # red and ir channels (raw)
    RED = X1[:, 4].T
    IR = X1[:, 5].T

    # if you're using the original Nihon Kohden probes, you'll want to flip
    # these around.
    if inv:
        RED_t = RED
        RED = IR
        IR = RED_t

    # baseline signal from which to calculate heart-rate
    RED_base = np.array(RED[1000:41000])  # np.array(RED[999:41000])
    IR_base = np.array(IR[1000:41000])  # np.array(IR[999:41000])
    welch_base = np.vstack((RED_base,IR_base))

    # powerspectrum
    # f, P = signal.welch(welch_base, fs=fs, nperseg=71, nfft=256)
    f, P = signal.welch(welch_base, fs=fs, nperseg=welch_base.shape[1]/4) # nperseg and nfft should be the same, make noverlap end with end of data

    bpm = f * 60

    # get heart-rate
    plt.figure('bpm vs P')
    # plt.plot(bpm, P)
    plt.plot(bpm.T, P[0,:])
    plt.plot(bpm.T, P[1,:])
    plt.title('select the center of the heart-rate peak')
    plt.xlim(12, 180)
    plt.ylim(0, 0.00005)
    plt.xlabel('frequency (beats per min).')
    ghr = plt.ginput(n=1, timeout=0, show_clicks=True)[0][0]
    fhr = ghr / 60
    plt.close('bpm vs P')

    ## Demodulate signal and compute the flux ratio and concentration.
    # get carrier signal from envelope (could also apply a bandpass filter)
    if filt_method == 'simple':
        fRED = signal.savgol_filter(-np.log(RED), 20, 3)
        fIR = signal.savgol_filter(-np.log(IR), 20, 3)
    elif filt_method == 'upenn':  # custom filter: upenn method (slow)
        fhwid = 0.10
        fl = (1 - fhwid) * fhr
        fh = (1 + fhwid) * fhr

        A_SB_inp = 60
        A_SB = 10.**(-A_SB_inp/20.)
        A_PB_inp = 1
        A_PB = (10. ** (A_PB_inp / 20.) - 1) / (10 ** (A_PB_inp / 20.) + 1) * 2
        A_SB2_inp = 60
        A_SB2 = 10. ** (-A_SB2_inp / 20.)
        # A_SB = 60
        # A_PB = 1
        # A_SB2 = 60

        (N_upenn, F_upenn, A_upenn, W_upenn) = \
            remezord([fl - 0.2, fl, fh, fh + 0.2], [1, 0, 1],
                     [A_SB, A_PB, A_SB2], Hz=fs)

        taps = signal.remez(N_upenn, F_upenn*fs, [0, 1, 0], weight=W_upenn,
                            fs=fs)
        fRED = signal.lfilter(taps, 1, -np.log(RED))
        fIR = signal.lfilter(taps, 1, -np.log(IR))
    else:
        raise NameError("Invalid filt_method")

    # find the peaks - min peak distance is defined as half the heart-rate    
    locsir, _ = signal.find_peaks(fIR, distance=round((0.5 / fhr) * fs))
    pksir = np.array(find_peak_heights(fIR, locsir))

    # find the troughs
    tir = np.zeros((1, len(locsir) - 1))         ##
    minir = np.zeros((1, len(locsir) - 1))       ##
    locsirmin = np.zeros((1, len(locsir) - 1))   ##
    pksir = pksir[0:len(pksir) - 1].T
    tmpt = np.array([i / fs for i in range(1, len(fIR) + 1)])
    for k in range(len(locsir) - 1):
        tir[0,k] = np.mean(tmpt[locsir[k]:locsir[k+1]])
        locsir_sublist = np.array(fIR[locsir[k]:locsir[k+1]])
        minir[0,k] = locsir_sublist.min()
        loctmp = np.where(locsir_sublist == minir[0,k])[0][0]
        locsirmin[0,k] = locsir[k] + loctmp - 1

    # interpolate red from IR peaks and troughs. uses scipy's interpolate
    # library
    f_interp = interpolate.interp1d(tmpt, fRED)
    pksred = f_interp(tmpt[locsir[0:len(locsir) - 1].tolist()])
    minred = f_interp(tmpt[[int(i) for i in locsirmin[0,:]]])

    # truncate in case some channels are shorter than others (by usually 1 or
    # 2)
    trunc = min([len(pksred[:]), len(minred[:]), len(pksir[:]),
                 len(minir[:].T)])
    pksred = pksred[0:trunc]
    pksir = pksir[0:trunc]
    minred = minred[0:trunc]
    minir = minir[0:trunc]

    # amplitude
    Ared = 0.5 * (pksred[:] - minred[:])
    Air = 0.5 * (pksir[:] - minir[:])

    eHbO2red, eHbred, _, eicg = getextinctioncoef(np.array([wv[0]]))
    eHbO2ir, eHbir, _, _ = getextinctioncoef(np.array([wv[1]]))

    eHbO2red = eHbO2red[0]
    eHbred = eHbred[0]
    eicg = eicg[0]
    eHbO2ir = eHbO2ir[0]
    eHbir = eHbir[0]

    # flux of light.
    # phi = Air / Ared

    # Probably bad, corrects for div/0. Fix later-------------------------------
    phi = np.array([])
    for i in range(len(Air.T)):
        if (Air[:,i] / Ared[i]) == np.inf:
            phi = np.append(phi, 0)
        else:
            phi = np.append(phi, Air[:,i] / Ared[i])
    #---------------------------------------------------------------------------

    I = np.logical_and(tir > tbl[0], tir < tbl[1])
    phi0 = np.mean(phi[I.reshape((len(I.T),))])  # choose a baseline Phi for d calculation.

    # distance of expansion, which is converted to concentration.
    d = phi0 * (eHbO2ir * SaO2 + eHbir * (1 - SaO2)) / (eHbO2red * SaO2 +
                                                        eHbred * (1 - SaO2))
    # find a d value to bring Ci to zero.
    Ci = (phi / d * (eHbO2ir * SaO2 + eHbir * (1 - SaO2)) - eHbO2red * SaO2 -
          eHbred * (1 - SaO2)) * tHb / eicg

    # iterpolate t and ca to the current temporal resolution of the SPY Elite,
    # which is fast enough preserve any features. sgolay filtering 51 x 3.
    t = np.linspace(tir[0,0], tir[0,-1], num=int(np.round(tir[0,-1] / 0.267)))

    cainterp = interpolate.PchipInterpolator(tir[0,:], Ci)
    ci_interp = cainterp(t)

    # interpolation to correct for nonlinearly spaced time points
    interp_ci = interpolate.interp1d(t, ci_interp)
    ci_result = interp_ci(np.linspace(t[0], t[-1], num=len(t)))

    Ca = signal.savgol_filter(ci_result, 51, 3)

    plt.figure("t,ca plot")
    plt.plot(t, Ca)
    plt.xlabel('time (sec)')
    plt.ylabel('Concentration (uM)')

    if savedata == 1:
        xout = np.hstack((t.reshape((len(t),1)),Ca.reshape((len(Ca),1))))

        # parse the filename of the input file to suggest where to save the
        # output and what to call it.
        slashloc = strfind(filename, "/")

        sugpath = filename[0:slashloc[-1]+1]
        fnamein = filename[slashloc[-1]+1:]

        emdashloc = strfind(fnamein, '_')
        fnameout = 'AIF_' + \
                   fnamein[(emdashloc[1]+1):(fnamein.find('.xls')-1)] + '.csv'

        # save file
        np.savetxt(sugpath + fnameout, xout, delimiter=",")

    return (t, Ca)


def strfind(string: str, elt: str) -> tuple:
    """
    Finds indices of a substring in a string

    :param string: string to be searched
    :param elt: single character to be found
    :return: tuple of indices where character is located
    """
    result = []
    length = len(string)
    for i in range(length):
        if elt == string[i]:
            result.append(i)

    return result


def find_peak_heights(data: list, indices: list) -> list:
    """
    Returns a list of the peak heights in data based on the indices of these
    peaks

    :param data: data in which peaks need to be found
    :param indices: list of indices where peaks appear
    :return: returns list of the heights of the peaks specified in indices
    """

    result = []
    for i in indices:
        result.append(data[i])

    return result