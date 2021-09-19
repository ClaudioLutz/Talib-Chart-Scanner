import yfinance as yf
import talib as tl
import pandas as pd
from flask import Flask, render_template, request
from patterns import patterns
import os,csv
from datetime import date
from dateutil.relativedelta import relativedelta

today = date.today()
three_yrs_ago = today - relativedelta(years=3)
first_day_yr_three_yrs_ago = date(three_yrs_ago.year, 1, 1)

app = Flask(__name__)

@app.route('/')
def index():
    pattern = request.args.get('pattern', None)
    stocks = {}

    with open('datasets/companies.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company': row[1]}
    print(stocks)

    if pattern:
        datafiles = os.listdir('datasets/daily')
        for dataset in datafiles:
            df = pd.read_csv('datasets/daily/{}'.format(dataset))
            pattern_function = getattr(tl, pattern)
            symbol = dataset.split('.')[0]
            try:
                result = pattern_function(df['Open'],df['High'],df['Low'],df['Close'])
                last = result.tail(1).values[0]
                if last > 0:
                    stocks[symbol][pattern] = 'bullish' 
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish' 
                else:
                    stocks[symbol][pattern] = None
            except:
                pass

    return render_template('index.html', patterns=patterns, stocks=stocks, current_pattern=pattern)

@app.route('/snapshot')
def snapshot():
    with open('datasets/companies.csv') as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]
            df = yf.download(symbol, start=first_day_yr_three_yrs_ago, end=today)
            df.to_csv('datasets/daily/{}.csv'.format(symbol))
    return {
        'code': 'success'
    }