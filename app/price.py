import os
from dotenv import load_dotenv
import requests
import pandas as pd
import json
from sklearn.linear_model import LinearRegression
import numpy as np
import math

load_dotenv()

API_KEY = "IY2I9IHI08ABKC3Z"

def pricefind(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}"
    r = requests.get(url).text
    r = json.loads(r)
    r = json.dumps(r['Time Series (Daily)'])
    df = pd.read_json(r, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index':'Date','1. open':'Open','2. high':'High','3. low':'Low','4. close':'Close','5. volume':'Volume'}, inplace=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return df

def stockinfo(symbol):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={API_KEY}"
    r = requests.get(url)
    r = r.json()
    name = r['Name']
    return name

def tstatcalc(df1,df2):
    df2['Diff'] = df2['Close'] - df1['Close']
    df2['Delta'] = df2['Diff'] - df2['Diff'].shift(-1)
    x = np.array(df2['Diff'][1:]).reshape((-1,1))
    y = np.array(df2['Delta'][:-1])
    model = LinearRegression().fit(x,y)
    df3 = pd.DataFrame()
    df3['Resids'] = pd.Series(y - model.predict(x)).values
    sresid = df3['Resids'].pow(2).sum()
    obs = len(df3['Resids'])
    sse = 1/(obs-2)*sresid
    xm = df2['Diff'].mean()
    xs = math.sqrt(1/((df2['Diff'] - xm)**2).sum())
    b1sse = sse * xs
    tstat = model.coef_/b1sse
    return tstat

def sharpe(df1,df2,lt,st,mhp):
    df2['Diff'] = df2['Close'] - df1['Close']
    df2['Delta'] = df2['Diff'] - df2['Diff'].shift(-1)
    df2 = df2.sort_values(by='Date')
    df2.drop(columns=['Open','High','Low','Close'],axis=1,inplace=True)
    df2['Trade'] = np.nan
    df2['Ret'] = df2['Delta'].shift(-1)/abs(df2['Diff'])
    df2['HP'] = 0
    df2 = df2.to_dict('records')
    for item in df2[:-1]:
        if item['Diff'] > st and item['HP'] == 0:
            item['Trade'] = -1
        elif item['Diff'] < lt and item['HP'] == 0:
            item['Trade'] = 1
    df2 = pd.DataFrame.from_dict(df2)
    for i in range(1,len(df2)-1):
        if df2.loc[i-1,'HP'] < mhp and df2.loc[i-1,'Trade'] != 0:
            df2.loc[i,'HP'] = df2.loc[i-1,'HP'] + 1
            df2.loc[i,'Trade'] = df2.loc[i-1,'Trade']
        elif df2.loc[i-1,'HP'] == mhp:
            df2.loc[i,'HP'] = 0
            df2.loc[i,'Trade'] = 0
    df2['TradeRet'] = df2['Ret'] * df2['Trade']
    ret = df2['TradeRet'].mean()
    stdev = df2['TradeRet'].std(skipna=True)
    sharpe = ret/stdev
    return sharpe

#Regex to validate ticker input
def tickercheck(inputString):
    return bool(re.search(r'^[A-Za-z]{1,5}$', inputString))


