from __future__ import absolute_import

import datetime
import io
import os
import time as t
from datetime import datetime, time

import pandas as pd
from prettytable import PrettyTable

from backtest import BackTest
from config import Config
from connection import SQLDB
from load import LoadTrade
from scraper import get_live_data


class Updater:
    def __init__(self):
        self.master_df=None
        self._l=LoadTrade()

    def load_data(self,filename='nasdaq.csv'):
        """use this function to seed the database"""
        data_path=os.path.join(os.getcwd(),Config.DATA_PATH,filename)
        self.master_df=pd.read_csv(data_path)

        for index,row in self.master_df.iterrows():
            try:
                print(f'processing {row["Symbol"]},{row["Name"]}')
                self._l.add_new_records(row['Symbol'],row['Name'],row['Volume'],row['Industry'],row['Sector'])
                # intentionally sleep to avoid any threshold limit
                t.sleep(2)
            except Exception as e:
                print(f"Exception occured during seeding the database {e}")

    def update_data(self,filename='nasdaq.csv'):
        """use this function to update the data"""
        data_path=os.path.join(os.getcwd(),Config.DATA_PATH,filename)
        self.master_df=pd.read_csv(data_path)

        for index,row in self.master_df.iterrows():
            try:
                print(f'updating {row["Symbol"]},{row["Name"]}')
                self._l.update_existing_records(row['Symbol'])
                # intentionally sleep to avoid any threshold limit
                t.sleep(2)
            except Exception as e:
                print(f"Exception occured during updating the records {e}")

if __name__=='__main__':
    u=Updater()
    u.update_data()
