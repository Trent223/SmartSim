import sys
import csv
import numpy as np
from math import *
from scipy.optimize import curve_fit

def do_optimization(model, args, x_data, y_data):
    func = eval("lambda {}:{}".format(args,model))

    popt, pcov = curve_fit(func, np.array(x_data), np.array(y_data))

    return popt
