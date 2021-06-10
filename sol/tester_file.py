#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 21:39:26 2021

@author: thomasusherwood
"""

from o_loadAIF import o_loadAIF
from DCEFI import DCEFI

dir = '/Users/thomasusherwood/lab_code/elliott_lab/PDD_project/IR-RED-AIF/data/'
fname = 'test1_test1'

d = DCEFI(dir,fname)
o_loadAIF(d)