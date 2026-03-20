from quanthero import IN_COLAB
import os
import pandas as pd
import gdown


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
            os.mkdir(db_path)

        self.path = db_path

    def get(self,fname):

        return pd.read_pickle(f"{self.path}/{fname}.pickle")