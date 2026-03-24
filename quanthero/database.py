from quanthero import IN_COLAB
import os
import pandas as pd
import gdown
import requests


class DataBase:

    def __init__(self):
        if IN_COLAB:
            if not os.path.exists('/content/drive/MyDrive'):
                from google.colab import drive
                drive.mount('/content/drive')
            db_path = '/content/drive/MyDrive/db'
        else:
            db_path = 'db'

        if not os.path.exists(db_path):
            gdown.download_folder(id='1q8ZHkAlUTYlbHArGNVTqjEbWhlOUiF0E',output=db_path)

        self.path = db_path

    def get(self,fname):

        return pd.read_pickle(f"{self.path}/{fname}.pickle")
    
    def get_klines(self,stock_id):

        parameter = {
            "dataset": "TaiwanStockPrice",
            "data_id": stock_id,
            "start_date": "2000-01-01",
        }
        r = requests.get("https://api.finmindtrade.com/api/v4/data",params=parameter)
        df = pd.DataFrame(r.json()['data']).rename(columns={'max':'high','min':'low','Trading_Volume':'volume'}).set_index('date')
        df.index = pd.to_datetime(df.index)
        df = df[['open','high','low','close','volume']]

        return df