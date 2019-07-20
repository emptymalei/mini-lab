import numpy as np
import random
import scipy.stats as scps
import pandas as pd

def cramers_v(x, y):

    if isinstance(x, list):
        x = np.array(x)
    if isinstance(y, list):
        y = np.array(y)

    confusion_matrix = pd.crosstab(x,y)
    chi2 = scps.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2/n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2-((k-1)*(r-1))/(n-1))
    rcorr = r-((r-1)**2)/(n-1)
    kcorr = k-((k-1)**2)/(n-1)
    return np.sqrt(phi2corr/min((kcorr-1),(rcorr-1)))

class CorrelationDataFaker(object):
    def __init__(self, x):
        self.x = x
        return super(CorrelationDataFaker, self).__init__()

    def _curves(self, sets=None, jitter_percent=None):
        if jitter_percent is None:
            jitter_percent = 0.05
        if sets is None:
            sets = [
                'linear+1', 'linear-1', 'vertical',
                'flat', 'concave', 'convex'
            ]
        elif isinstance(sets, str):
            sets = [sets]

        dispatcher = {
            'linear+1': self.__linearp1,
            'linear-1': self.__linearm1,
            'vertical': self.__vertical,
            'flat': self.__flat,
            'concave': self.__concave,
            'convex': self.__convex
        }

        res = {}
        jitter_scale = np.median(self.x)*jitter_percent
        for name, func in dispatcher.items():
            func_x, func_y = func(self.x)
            func_x = [
                i + self._jitter(jitter_scale) for i in func_x
                ]
            func_y = [
                i + self._jitter(jitter_scale) for i in func_y
                ]
            res[name] = {
                'x': func_x,
                'y': func_y
            }

        return res

    def _jitter(self, scale):
        return random.random() * scale

    def __linearp1(self, x):
        return (x, x)

    def __linearm1(self, x):
        return (x, -x)

    def __vertical(self, x):
        return (
            np.linspace(
                np.median(x), np.median(x), len(x)
            ),
            x)

    def __convex(self, x):
        return (x, (x - np.median(x))**2)

    def __concave(self, x):
        return (x, -(x - np.median(x))**2)

    def __flat(self, x):
        return (
            x,
            np.linspace(
                np.median(x), np.median(x), len(x)
            ))