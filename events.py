__author__ = 'alex'

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import csv


def find_events_below_X(ls_symbols, d_data, X, output_orders_file, HOLD_DAYS=5, BUY_NUM = 100):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']
    with open(output_orders_file, "w") as orders_file:
        orders_writer = csv.writer(orders_file, delimiter=',')
        print "Finding Events"
        # Creating an empty dataframe
        df_events = copy.deepcopy(df_close)
        df_events = df_events * np.NAN
        # Time stamps for the event range
        ldt_timestamps = df_close.index
        total_events = 0
        print ldt_timestamps
        for s_sym in ls_symbols:
            for i in range(1, len(ldt_timestamps)):
                # Calculating the returns for this timestamp
                f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
                f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
                #f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
                #f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
                #f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
                #f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

                # Event is found if the symbol is down more then 3% while the
                # market is up more then 2%
                #if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
                #    df_events[s_sym].ix[ldt_timestamps[i]] = 1
                if f_symprice_today < X and f_symprice_yest >= X :# and s_sym not in found_syms:
                    df_events[s_sym].ix[ldt_timestamps[i]] = 1
                    total_events += 1
                    orders_writer.writerow([ldt_timestamps[i].year, ldt_timestamps[i].month, ldt_timestamps[i].day, s_sym, "Buy", BUY_NUM])
                    sell_date = ldt_timestamps[i + HOLD_DAYS]
                    orders_writer.writerow([sell_date.year, sell_date.month, sell_date.day, s_sym, "Sell", BUY_NUM])



    print "Found total events %i" % total_events
    return df_events


def e_profiler(dt_start, dt_end, year, price, output_file):
    print "For date range %s to %s , for SP500 year %s " % (dt_start, dt_end, year)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    ls_symbols = dataobj.get_symbols_from_list('sp500' + year)
    ls_symbols.append('SPY')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
        d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events_below_X(ls_symbols, d_data, price, output_file)
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=10, i_lookforward=10,
                     s_filename='MyEventStudy%s%s.pdf' % (year, price), b_market_neutral=True, b_errorbars=True,
                     s_market_sym='SPY')


if __name__ == '__main__':
    #
    # dt_start = dt.datetime(2008, 1, 1)
    # dt_end = dt.datetime(2009, 12, 31)
    # e_profiler(dt_start, dt_end, "2008", 5)
    #
    # dt_start = dt.datetime(2008, 1, 1)
    # dt_end = dt.datetime(2009, 12, 31)
    # e_profiler(dt_start, dt_end, "2012", 5)
    #
    #
    # dt_start = dt.datetime(2008, 1, 1)
    # dt_end = dt.datetime(2009, 12, 31)
    # e_profiler(dt_start, dt_end, "2008", 10)


    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    e_profiler(dt_start, dt_end, "2012", 5, "my_orders.csv")
