import shioaji as sj
import pandas as pd

from quanthero.database import DataBase


class Account:

    def __init__(self,api_key,secret_key,simulation=False):

        self.api = sj.Shioaji(simulation)
        self.accounts = self.api.login(api_key,secret_key)

    def check(self):

        if self.api.simulation:

            contract = self.api.Contracts.Stocks["2890"]
            order = sj.order.StockOrder(
                action='Buy',
                price=contract['limit_down'],
                quantity=1,
                price_type='LMT',
                order_type='ROD',
            )
            trade = self.api.place_order(contract=contract,order=order)
            print('\nAuth success !')

    def get_realtime_data(self,stock_ids:list):

        contracts = [self.api.Contracts.Stocks[stock_id] for stock_id in stock_ids]
        contracts = [contract for contract in contracts if contract is not None]
        snapshots = self.api.snapshots(contracts)

        info = pd.DataFrame(s.__dict__ for s in contracts).set_index('code')
        df = pd.DataFrame(s.__dict__ for s in snapshots).set_index('code')

        df['ts'] = pd.to_datetime(df['ts'])
        df.insert(0,'name',info['name'])

        return df