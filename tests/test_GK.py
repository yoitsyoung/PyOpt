from ..PyOpt import GK
import pytest
import numpy as np

def test_call_price_accuracy():
    call = GK(1.3311, 1.3, 1, 0.0010, 0.0002, 0.08, True, False)
    assert call.price == 0.058661841

def test_put_price_accuracy():
    put = GK(1.3311, 1.3, 1, 0.0010, 0.0002, 0.08, False, False)
    assert put.price == 0.028632302

#def test_ivol_accuracy():

#def test_edge_cases():

def test_put_call_parity():
    S = 1.3311
    K = 1.3
    T = 1
    r1 = 0.0010
    r2 = 0.0002
    vol = 0.08
    call = GK(S, K, T, r1, r2, vol, True, False)
    put = GK(S, K, T, r1, r2, vol, False, False)
    assert call.price - put.price == S * np.exp(-r1 * T) - K * np.exp(-r2 * T)

def test_vol_price_equivalence():
    S = 1.3311
    K = 1.3
    T = 1
    r1 = 0.0010
    r2 = 0.0002
    vol = 0.08
    call = GK(S, K, T, r1, r2, vol, True, False)
    assert call.price == GK(S, K, T, r1, r2, call._vol, True, False).price

#def test_infinite_vol():
