__author__ = 'alex'

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas
from pylab import *

def calc_bollinger(symbols, startday, endday, PERIOD = 20):
    '''
        Calculate bollinger bands for a stock and plot them

    '''

    timeofday=dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startday, endday, timeofday)

    dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    voldata = dataobj.get_data(timestamps, symbols, "volume")
    adjcloses = dataobj.get_data(timestamps, symbols, "close")
    actualclose = dataobj.get_data(timestamps, symbols, "actual_close")

    adjcloses = adjcloses.fillna()
    adjcloses = adjcloses.fillna(method='backfill')

    means = pandas.rolling_mean(adjcloses, PERIOD, min_periods=20)
    stds = pandas.rolling_std(adjcloses, PERIOD, min_periods=20)
    upper_bolinger = means + stds
    lower_bolinger = means - stds
    bollinger_val = (adjcloses - means) / (stds)
    print bollinger_val[symbols[0]]

    # Plot the prices
    plt.clf()

    symtoplot = symbols[0]
    plot(adjcloses.index, adjcloses[symtoplot].values, label=symtoplot)
    plot(adjcloses.index, upper_bolinger[symtoplot].values)
    plot(adjcloses.index, lower_bolinger[symtoplot].values)
    plot(adjcloses.index, means[symtoplot].values)

    plt.legend([symtoplot, 'Moving Avg.'])
    plt.ylabel('Adjusted Close')

    savefig("bollinger_bands.png", format='png')
if __name__ == '__main__':
    stock_syms = ["AAPL"]
    start_dt = dt.datetime(year=2010, month=1, day=1)
    end_dt = dt.datetime(year=2010, month=12, day=31)
    period = 20
    calc_bollinger(stock_syms, start_dt, end_dt, period)
