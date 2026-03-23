import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
import sys
import time
import pickle
import warnings

from quanthero.database import DataBase


warnings.filterwarnings('ignore')


def crawl_price(date):

    date_format =  pd.to_datetime(date).strftime('%Y%m%d')

    url = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date=%s&type=ALLBUT0999&response=json"%(date_format)
    r = requests.get(url)

    if r.json()['stat'].lower() == 'ok':
        tables = r.json()['tables']
        data = [t for t in tables if 'data' in t.keys() and len(t['data']) > 500][0]
        sii = pd.DataFrame(data['data'],columns=data['fields'])
        sii.columns = sii.columns.to_series().apply(lambda s:s.replace(' ','')).tolist()

        cols = ['開盤價','最高價','最低價','收盤價','成交股數','成交金額','成交筆數']

        sii = sii.astype(str).replace(',','',regex=True)

        for col in cols:
            sii[col] = pd.to_numeric(sii[col],errors='coerce')

        sii = sii[['證券代號'] + cols]

        # OTC
        url = "https://www.tpex.org.tw/www/zh-tw/afterTrading/dailyQuotes"
        payload = {
            'date':pd.to_datetime(date).strftime('%Y/%m/%d'),
            'response':'json'
        }
        r = requests.post(url,data=payload)
        tables = r.json()['tables']
        data = [t for t in tables if 'data' in t.keys() and len(t['data']) > 500][0]
        otc = pd.DataFrame(data['data'],columns=data['fields'])
        otc.columns = otc.columns.to_series().apply(lambda s:s.replace(' ','').replace('(元)','')).tolist()
        otc = otc.rename(columns={'代號':'證券代號','收盤':'收盤價','開盤':'開盤價','最高':'最高價','最低':'最低價'})

        otc = otc.astype(str).replace(',','',regex=True)
        for col in cols:
            otc[col] = pd.to_numeric(otc[col],errors='coerce')

        otc = otc[['證券代號'] + cols]

        # merge
        dfs = pd.concat([sii,otc])
        dfs = dfs[dfs['證券代號'].apply(lambda s:len(s) == 4)]
        dfs['date'] = pd.to_datetime(date)
        dfs = dfs.mask(dfs == 0,np.nan)

    else:
        dfs = pd.DataFrame()

    return dfs


def crawl_basic_info():

    dfs = pd.DataFrame()
    for market in ['sii','otc']:
        payload = {
            'encodeURIComponent':1,
            'step':1,
            'firstin':1,
            'TYPEK':market
        }
        r = requests.post('https://mopsov.twse.com.tw/mops/web/ajax_t51sb01',data=payload)
        dfs = pd.concat([dfs,pd.read_html(r.text)[0]])

    dfs = dfs.rename(columns=lambda s:s.replace(' ','')).rename(columns={'公司代號':'證券代號','公司簡稱':'name','產業類別':'category'})
    dfs = dfs[dfs['證券代號'].apply(lambda s:s.replace(' ','').isdigit())].set_index('證券代號')
    dfs = dfs[['name','category']]
    dfs.index = dfs.index.astype(str)

    return dfs


def auto_update():

    db = DataBase()

    sdate = db.get('成交股數').index[-1] + pd.DateOffset(days=1)
    edate = pd.to_datetime('now')

    dates = pd.date_range(sdate,edate)

    with tqdm(total=len(dates),desc='crawling',file=sys.stdout) as pbar:

        for date in dates:

            new = crawl_price(date)

            if not new.empty:
                for fname in new.columns.drop(['證券代號','date']):
                    old = db.get(fname)
                    dfs = pd.concat([old,new.pivot_table(fname,'date','證券代號')]).groupby(level=0).nth[-1].sort_index().sort_index(axis=1)
                    # dfs.to_pickle(f"{db.path}/{fname}.pickle")

                    with open(f"{db.path}/{fname}.pickle",'wb') as f:
                        pickle.dump(dfs,f)

                pbar.write(f"{date.strftime('%Y-%m-%d')} ✅")
            else:
                pbar.write(f"{date.strftime('%Y-%m-%d')} ❌")

            pbar.update(1)
            time.sleep(3)

    info = pd.concat([db.get('基本資料'),crawl_basic_info()]).groupby(level=0).last()
    
    with open(f"{db.path}/基本資料.pickle",'wb') as f:
        pickle.dump(info,f)