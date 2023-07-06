import warnings
import scipy as sp
from scipy.stats import norm
import numpy as np

class GK:
    def __init__(self, S, K, T, r1, r2, inputVol = None, isCall = True, inputPrice = None):
        if K == 0:
                raise ZeroDivisionError('The strike price cannot be zero')
        self.isCall = isCall
        self.S = S
        self.K = K
        self.T = T
        self.r1 = r1
        self.r2 = r2
        self.inputVol = bool(inputVol)
        self.inputPrice = bool(inputPrice)

        if inputVol and inputPrice:
            raise ValueError('Cannot have both inputVol and inputPrice')
        if inputVol:
            self._vol = inputVol
        if inputPrice:
            self._price = inputPrice


        #if callPrice:

        #if putPrice:

    #price getter and setter functions
    @property
    def d1(self):
        return (np.log(self.S/self.K) + (self.r2 - self.r1 + 0.5 * self._vol**2) * self.T) / (self._vol * np.sqrt(self.T))

    @property
    def d2(self):
        return (self.d1 - self._vol * np.sqrt(self.T))

    @property
    def price(self):
        if self.inputVol:
            if self._vol == 0 or self.T == 0:
                call = max(0.0, self.S - self.K)
                put = max(0.0, self.K - self.S)
            if self.isCall:
                call = self.S * np.exp(-self.r1 * self.T) * sp.stats.norm.cdf(self.d1) - self.K * np.exp(-self.r2 * self.T) * sp.stats.norm.cdf(self.d2)
                return call
            if not self.isCall:
                put =self.K * np.exp(-self.r2 * self.T) * sp.stats.norm.cdf(-self.d2) - self.S * np.exp(-self.r1 * self.T) * sp.stats.norm.cdf(-self.d1)
                return put

        if self.inputPrice:
            return self._price

    @price.setter
    def price(self, value):
        self._price = value
        self.inputPrice = True
        self.inputVol = False

    # We implement the Newton-Raphson method to compute the implied volatility. Further optimizations with regard to the starting point of the guesstimate can be done
    @property
    def vol(self):
        if self.inputVol:
            return self._vol
        if self.inputPrice:
            vol_estimate = 0.05
            target_price = self._price
            for i in range(100):
                option = GK(self.S, self.K, self.T, self.r1, self.r2, vol_estimate, self.isCall, False)
                print(option.price)
                print(target_price)
                vol_estimate = vol_estimate - (option.price/self.S - target_price/self.S) / option.vega
                print (vol_estimate)
            self._vol = vol_estimate
            return self._vol

    #TODO: Conduct tests for vol and price setter functions
    #TODO: Figure out how to deal with infinite vol when ATM option is almost expiring and price is positive

    @vol.setter
    def vol(self, value):
        self._vol = value
        self.inputPrice = False
        self.inputVol = True


    # we use Finite Difference method to compute the greeks
    @property
    def delta(self, S_flex = None ):
        if S_flex == None:
            S_flex = 0.0000000001*self.S

        optionU = GK(self.S + S_flex, self.K, self.T, self.r1, self.r2, self.vol, self.isCall)
        optionD = GK(self.S - S_flex, self.K, self.T, self.r1, self.r2, self.vol, self.isCall)
        delta = (optionU.price - optionD.price) / (2 * S_flex)
        return delta


    # The Finite Difference method for second order deirvatives is given by the Central Difference method
    @property
    def gamma(self, S_flex = None):
        if S_flex == None:
            S_flex = 0.0000000001*self.S

        optionU = GK(self.S + S_flex, self.K, self.T, self.r1, self.r2, self.vol, self.isCall)
        optionD = GK(self.S - S_flex, self.K, self.T, self.r1, self.r2, self.vol, self.isCall)
        gamma = (optionU - 2 * self.price + optionD) / (S_flex**2)
        return gamma

    #Greeks in Garman and Kohlhagen model are often quoted in terms of CCY1 notional. Hence we divide by the spot price
    @property
    def vega(self, vol_flex = None):
        if vol_flex == None:
            vol_flex = 0.0000000001*self._vol

        optionU = GK(self.S, self.K, self.T, self.r1, self.r2, self.vol + vol_flex, self.isCall)
        optionD = GK(self.S, self.K, self.T, self.r1, self.r2, self.vol - vol_flex, self.isCall)
        vega =  (optionU.price - optionD.price) / (2 * vol_flex) / self.S
        return vega

class Position(list):
    def delta(self, S_flex = None):
        return sum([option.delta for option in self])

    def gamma(self, S_flex = None):
        return sum([option.gamma for option in self])

    def vega(self, vol_flex = None):
        return sum([option.vega for option in self])

