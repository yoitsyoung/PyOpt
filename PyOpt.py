import warnings
import scipy as sp
from scipy.stats import norm
import numpy as np

class GK:
    def __init__(self, S, K, T, r1, r2, vol = None, isCall = True, callPrice = None, putPrice = None):
        self.isCall = isCall
        self.S = S
        self.K = K
        self.T = T
        self.r1 = r1
        self.r2 = r2
        self.vol = vol


        #if callPrice:

        #if putPrice:


    def price(self):
        if self.vol:
            if self.vol == 0 or self.T == 0:
                call = max(0.0, self.S - self.K)
                put = max(0.0, self.K - self.S)
            if self.K == 0:
                raise ZeroDivisionError('The strike price cannot be zero')
            else:
                self.d1 = (np.log(self.S/self.K) + (self.r2 - self.r1 + 0.5 * self.vol**2) * self.T) / (self.vol * np.sqrt(self.T))
                self.d2 = self.d1 - self.vol * np.sqrt(self.T)
            if self.isCall:
                call = self.S * np.exp(-self.r1 * self.T) * sp.stats.norm.cdf(self.d1) - self.K * np.exp(-self.r2 * self.T) * sp.stats.norm.cdf(self.d2)
                return call
            if not self.isCall:
                put =self.K * np.exp(-self.r2 * self.T) * sp.stats.norm.cdf(-self.d2) - self.S * np.exp(-self.r1 * self.T) * sp.stats.norm.cdf(-self.d1)
                return put

    # we use Finite Difference method to compute the greeks
    def delta(self, S_flex = None ):
        if S_flex == None:
            S_flex = 0.0000000001*self.S

        optionU = GK(self.S + S_flex, self.K, self.T, self.r1, self.r2, self.vol, self.isCall)
        optionD = GK(self.S - S_flex, self.K, self.T, self.r1, self.r2, self.vol, self.isCall)
        delta = (optionU.price() - optionD.price()) / (2 * S_flex)
        return delta


    # The Finite Difference method for second order deirvatives is given by the Central Difference method
    def gamma(self, S_flex = None):
        if S_flex == None:
            S_flex = 0.0000000001*self.S

        optionU = GK(self.S + S_flex, self.K, self.T, self.r1, self.r2, self.vol, self.isCall)
        optionD = GK(self.S - S_flex, self.K, self.T, self.r1, self.r2, self.vol, self.isCall)
        gamma = (optionU - 2 * self.price() + optionD) / (S_flex**2)
        return gamma

    # We quote vega as a change in option price as a % of r1 currency for a 1% move in implied volatility
    def vega(self, vol_flex = None):
        if vol_flex == None:
            vol_flex = 0.0000000001*self.vol

        optionU = GK(self.S, self.K, self.T, self.r1, self.r2, self.vol + vol_flex, self.isCall)
        optionD = GK(self.S, self.K, self.T, self.r1, self.r2, self.vol - vol_flex, self.isCall)
        vega = 0.01 * (optionU.price() - optionD.price()) / (2 * vol_flex) / self.S
        return vega

class Position(list):
    def delta(self, S_flex = None):
        return sum([option.delta() for option in self])

    def gamma(self, S_flex = None):
        return sum([option.gamma() for option in self])

    def vega(self, vol_flex = None):
        return sum([option.vega() for option in self])
