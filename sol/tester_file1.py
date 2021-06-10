#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 21:39:26 2021

@author: thomasusherwood
"""

from o_loadAIF import o_loadAIF
from DCEFI import DCEFI

if __name__ == '__main__':
    dir = '/Users/thomasusherwood/lab_code/elliott_lab/PDD_project/Dye-Densitometer/data/'
    fname = 'test1_test1'

    d = DCEFI(dir,fname)
    o_loadAIF(d)

