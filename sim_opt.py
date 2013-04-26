__author__ = 'alex'

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import math
import datetime as dt
import numpy as np
from math import sqrt
import pandas as pd
from copy import deepcopy
import matplotlib.pyplot as plt



def simulate(startdate, enddate, stocks, alloc):
    """

       return std_daily,daily_mean,sharpe,cum_ret

    """
    print "================="
    print alloc
    print stocks
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, stocks, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    na_price = d_data['close'].values
    na_normalized_price = na_price / na_price[0, :]
    na_alloc = na_normalized_price * alloc
    na_rets = deepcopy(na_alloc)
    daily_values = na_rets.sum(axis=1)
    dv1 = daily_values.copy()
    tsu.returnize0(dv1)
    #Average daily return of the total portfolio
    f_mean = np.mean(dv1)
    print "Average Daily Returns Mean: %f" % f_mean
    #Standard deviation of daily returns of the total portfolio
    f_std = np.std(dv1)
    print "Std : %f" % f_std
    #Sharpe ratio (Always assume you have 252 trading days in an year. And risk free rate = 0) of the total portfolio
    f_sharpe = (f_mean * 252 - 0) / (f_std * np.sqrt(252))
    print "Sharpe : %f" % f_sharpe
    #Cumulative return of the total portfolio
    cum_ret = (((na_price[-1] - na_price[0]) / na_price[0]) * alloc).sum() + 1
    print "Cumalative return %f" % cum_ret
    print "=================="
    return f_std, f_mean, f_sharpe, cum_ret

def optimize(dt_start, dt_end, stocks):
    """
        optimize allocation of 4 stocks in portfolio , with best Sharpe ratio
        steps of 0.1
        TODO use fmin
    """
    best = 0
    r_a = r_b = r_c = r_d = 0
    for a in np.arange(0,1.1,0.1):
        for b in np.arange(0,1.1,0.1):
            for c in np.arange(0,1.1,0.1):
                for d in np.arange(0,1.1,0.1):
                    if (a + b + c + d) == 1:
                        f_std, f_mean, f_sharpe, cum_ret = simulate(dt_start, dt_end, stocks, [a, b, c, d])
                        if f_sharpe > best:
                            best = f_sharpe
                            r_a = a
                            r_b = b
                            r_c = c
                            r_d = d

    print "--------Best Sharpe %f-------------" % best
    print r_a, r_b, r_c, r_d
    return best, r_a, r_b, r_c, r_d


if __name__ == '__main__':
    #test1
    #dt_start = dt.datetime(2010, 1, 1)
    #dt_end = dt.datetime(2010, 12, 31)
    #simulate(dt_start, dt_end, ['AXP', 'HPQ', 'IBM', 'HNZ'], [0.0, 0.0, 0.0, 0.1])

    #test2
    #dt_start = dt.datetime(2011, 1, 1)
    #dt_end = dt.datetime(2011, 12, 31)
    #simulate(dt_start, dt_end, ['AAPL', 'GLD', 'GOOG', 'XOM'], [0.4, 0.4, 0.0, 0.2])
    #optimize(dt_start, dt_end, ['AAPL', 'GLD', 'GOOG', 'XOM'])

    #1
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)
    optimize(dt_start, dt_end, ['C', 'GS', 'IBM', 'HNZ'])



