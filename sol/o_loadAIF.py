#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 10:12:36 2020

@author: thomasusherwood
"""

import os
import csv
import numpy as np
from TI_to_AIF import TI_to_AIF
from pandas import read_csv
import matplotlib.pyplot as plt
import DCEFI
from typing import List

def o_loadAIF(d: DCEFI, saveflag: int = 1):
    """

    :param d: DCE-FI datastructure containing information about the saved file
    :param saveflag: determines if file should be saved
    :return: None
    """

    # first, check to see whether .aif is there
    pred_file = d.fname[0:max(strfind(d.fname,'_'))] + '.aif'
    
    # if the .aif file exists, load it.
    if (os.path.exists(d.dir+pred_file)) and \
        (os.path.splitext(d.dir+pred_file)[-1].lower() in \
        [".m" ".mlx" ".mlapp" ".mat" ".fig" ".txt"]) and (saveflag != 2):
        # load the aif file
        M = np.array(read_csv(d.dir+pred_file, sep=',',header=None))
        
        d.aif = M[:,1].T
    else:
        aif_path = np.array([])
        files = os.listdir(d.dir)
        for i in range(2,len(files)):
            if 'Volts' in files[i]:
                aif_path = np.append(aif_path, d.dir + files[i])
        
        if len(aif_path) == 0: # if a file couldn't be found
            # dlg "Could not locate the AIF file"
            raise FileNotFoundError("Could not locate a .aif file or a " + \
                                    "Volts file")
        else: # file was found with 'Volts' in it.
            filename = aif_path[0]

            wv = [804, 938] # wavelength of probe LEDs.
    
            # run TI_to_AIF and save
            filt_method = 'upenn' # upenn is best, simple is faster.
            (t, Ca) = TI_to_AIF(filename, wv, False, filt_method, 0)
    
            # select relevant portion of the curve
            clicks = plt.ginput(n=2, timeout=0, show_clicks=True)
            xmin = min(clicks[0][0],clicks[1][0])
            ymin = min(clicks[0][1],clicks[1][1])
            width = abs(max(clicks[0][0],clicks[1][0])-xmin)
            height = abs(max(clicks[0][1],clicks[1][1])-ymin)
            pos = np.array([xmin, ymin, width, height])
            
            # crop to the approprate part.
            x1 = find(t > pos[0],True)
            x2 = find(t > pos[0]+pos[2],True)

            t_cropped = t[x1-1:x2]-t[x1]
            t_cropped = t_cropped.reshape((len(t_cropped),1))
            Ca_cropped = Ca[x1-1:x2]
            Ca_cropped = Ca_cropped.reshape((len(Ca_cropped), 1))
            csv_matrix = np.hstack((t_cropped,Ca_cropped))
            
            # if option 0 was chosen, do not save a .aif file, otherwise do.
            if saveflag != 0:
                with open(d.dir+pred_file, 'w') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    for r in range(len(csv_matrix)):
                        csvwriter.writerow(csv_matrix[r,:])
            
    
def strfind(string: str, elt: str) -> tuple:
    """
    Finds indices of a single character in a string

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