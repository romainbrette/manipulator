'''
Autofocus algorithms
'''
import cv2
import numpy as np
from tipdetection import *
from templatematch import *
from scipy.optimize import minimize_scalar

__all__ = ['tip_autofocus']

def tip_autofocus(focus, min = None, max = None):
    '''
    Focus on the tip.

    Parameters
    ----------
    focus : focus function, argument = z, current position being z = 0, returns image
    min : minimum z
    max : maximum z
    '''
    # Uses corner detection
    res = minimize_scalar(lambda x : -tip_detection(focus(x))[2], bounds = (min, max),
                          method = 'Bounded') # uses Brent method
