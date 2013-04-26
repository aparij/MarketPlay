from apt_pkg import init

__author__ = 'alex'

import sys
import csv
import pandas as pd
import numpy as np
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import datetime as dt
from collections import OrderedDict

def generate_dates_range(start, end):
    '''
        return a list containing dates range as keys
    '''

    total_days = (end - start).days
    print start, end, total_days
    date_list = [end - dt.timedelta(days=x) for x in range(0, total_days + 1)]
    date_list.reverse()
    return date_list

def main(initial_cash, orders_csv, values_csv):
    '''

        Load a csv containing a market orders of buy,sell and initial cash and export
        a list of dates and total value of money in the end of the last date
    '''
    dates = set()
    stocks = set()
    orders = {}
    with open(orders_csv, "rU") as orders_file:
        orders_reader = csv.reader(orders_file, delimiter=',')
        for line in orders_reader:
            stocks.add(line[3])
            order_date = dt.datetime(int(line[0]), int(line[1]), int(line[2]), 16)
            dates.add(order_date)
            orders.setdefault(order_date, [])
            #stocl, type order , amount
            orders[order_date].append((line[3], line[4], line[5]))
    dates_list = list(dates)
    dates_list.sort()
    dates_range = generate_dates_range(dates_list[0], dates_list[-1])
    ldt_timestamps = du.getNYSEdays(dates_list[0], dates_list[-1], dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, stocks, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    equities = {}
    daily_totals = []
    daily_returns = []
    with open(values_csv, "w") as values_file:
        values_writer = csv.writer(values_file, delimiter=',')
        for d in dates_range:
            r = [d.isoformat()]
            if d in orders:
            #there is a transaction on this date
                for ord in orders[d]:
                    stock = ord[0]
                    type = ord[1]
                    amount = int(ord[2])
                    working_date = d
                    while working_date not in d_data['close'][stock]:
                        working_date = working_date + dt.timedelta(days=1)
                        if working_date == dt.datetime(year=2009, month=12, day=28, hour=16):
                            working_date = None
                            break
                    if working_date is None:
                        working_date = d - dt.timedelta(days=1)
                        while working_date not in d_data['close'][stock]:
                             working_date = working_date - dt.timedelta(days=1)
                             break
                    total = d_data['close'][stock][working_date] * amount
                    if type == "Sell":
                        initial_cash += total
                        equities[stock] = equities.setdefault(stock, 0) - amount
                        if equities[stock] == 0:
                            del equities[stock]
                    elif type == "Buy":
                        initial_cash -= total
                        equities[stock] = equities.setdefault(stock, 0) + amount
                    else:
                        print "Wrong type of transaction %s" % type
                v = initial_cash
                for k in equities.iterkeys():
                    v += equities[k] * d_data['close'][k][working_date]
                r.append(v)
            else:
            #no transaction , just update with the current stock prices + cache
                v = initial_cash
                for k in equities.iterkeys():
                    if d in d_data['close'][k]:
                        #dates with stock market open
                        v += equities[k] * d_data['close'][k][d]
                    else:
                        v = None
                r.append(v)
            if r[1] and r[1]!=0:
                daily_totals.append(r[1])
                if len(daily_totals) > 1:
                    daily_returns.append((daily_totals[-1] * 1.0 / daily_totals[-2] * 1.0) -1)
            values_writer.writerow(r)
        print daily_returns
        print daily_totals
        nmp = np.array(daily_returns)
        #Average daily return of the total portfolio
        f_mean = nmp.mean(axis=0)
        print "Average Daily Returns Mean: %f" % f_mean
        #Standard deviation of daily returns of the total portfolio
        f_std = nmp.std(axis=0)
        print "Std : %f" % f_std
        #Sharpe ratio (Always assume you have 252 trading days in an year. And risk free rate = 0) of the total portfolio
        f_sharpe = (f_mean * 252 - 0) / (f_std * np.sqrt(252))
        print "Sharpe : %f" % f_sharpe
if __name__ == '__main__':
    """
        example of orders_csv row

             Year,Month,Day,Symbol,BUY or SELL,Number of Shares
            2008, 12, 3, AAPL, BUY, 130
            2008, 12, 8, AAPL, SELL, 130
            2008, 12, 5, IBM, BUY, 50
    """

    print sys.argv
    initial_cash = int(sys.argv[1])
    orders_csv = sys.argv[2]
    values_csv = sys.argv[3]
    main(initial_cash, orders_csv, values_csv)

