#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 10:57:29 2020

@author: thomasusherwood
"""
import numpy as np
from pandas import read_csv
from typing import List


def getextinctioncoef(lambdas: List[int]) -> tuple:
    """

    :param lambdas:
    :return:
    """

    # can change to loadtxt if not just array of floats
    hemoglobin = np.array(read_csv('../data/hemoglobin.dat',
                                   delim_whitespace=True, header=None))

    indH = np.zeros(lambdas.shape)
    for tt in range(len(lambdas)):
        indH[tt] = find(hemoglobin[:, 0], lambdas[tt])
    indH = indH.astype(int)

    eHBO2 = hemoglobin[indH, 1] * np.log(10) * 10 ** -6
    eHB = hemoglobin[indH, 2] * np.log(10) * 10 ** -6

    # can change to loadtxt if not just array of floats
    newwater = np.array(read_csv('../data/newwater.dat', delim_whitespace=True,
                                 header=None))

    indW = np.zeros(lambdas.shape)
    for tt in range(len(lambdas)):
        indW[tt] = find(newwater[:, 0], lambdas[tt])
    indW = indW.astype(int)

    muaw = newwater[indW, 1]

    # can change to loadtxt if not just array of floats
    icg = np.array(read_csv('../data/icg.dat', delim_whitespace=True,
                            header=None))

    indicg = np.zeros(lambdas.shape)
    for tt in range(len(lambdas)):
        if lambdas[tt] <= 900:
            indicg[tt] = find(icg[:, 0], lambdas[tt])
        else:
            indicg[tt] = np.nan
    indicg = indicg.astype(int)

    eicg = np.zeros(eHB.shape)
    I = indicg < 0
    I_not = np.logical_not(I)
    eicg[I] = 0
    eicg[I_not] = icg[indicg[I_not], 1] * np.log(10) * 10 ** -6

    return (eHBO2, eHB, muaw, eicg)


def find(lst: List[float], elt: float) -> int:
    """
    Finds the index of the first instance of an element in a list

    :param lst: list to be searched
    :param elt: element to be found
    :return: int index of the first instance of elt
    """
    for i in range(len(lst)):
        if elt == lst[i]:
            return i
