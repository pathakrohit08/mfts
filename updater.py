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
from utilities import send_email


class Updater:
    def __init__(self):
        self.master_df=None
        self._l=LoadTrade()
        self.tickrs=["AMC","GME","FB","CLNE"]
        data_path=os.path.join(os.getcwd(),Config.DATA_PATH,"holidays.csv")
        self.holidays_df=pd.read_csv(data_path)

    def load_data(self,filename='nasdaq.csv'):
        """use this function to seed the database"""
        data_path=os.path.join(os.getcwd(),Config.DATA_PATH,filename)
        self.master_df=pd.read_csv(data_path)

        for index,row in self.master_df.iterrows():
            try:
                #if row["Symbol"] not in self.tickrs:continue
                print(f'processing {row["Symbol"]},{row["Name"]}')
                self._l.add_new_records(row['Symbol'],row['Name'],row['Volume'],row['Industry'],row['Sector'])
                # intentionally sleep to avoid any threshold limit
                t.sleep(2)      
            except Exception as e:
                print(f"Exception occured during seeding the database {e}")

        send_email("Initial load of data was complete","Load Data")

    def update_data(self,filename='nasdaq.csv'):
        """use this function to update the data"""
        data_path=os.path.join(os.getcwd(),Config.DATA_PATH,filename)
        self.master_df=pd.read_csv(data_path)

        for index,row in self.master_df.iterrows():
            try:
                #if row["Symbol"] not in self.tickrs:continue
                print(f'updating {row["Symbol"]},{row["Name"]}')
                self._l.update_existing_records(row['Symbol'])
                # intentionally sleep to avoid any threshold limit
                t.sleep(2)
            except Exception as e:
                print(f"Exception occured during updating the records {e}")

        send_email("Update of data was complete","Update Data")


    def perform_backtest(self):
        """use this function to perform backtest"""
        current_date=datetime.now().strftime('%m-%d-%Y') 
        if  current_date in self.holidays_df.Date.to_list():
            print("Market is closed for today")
            return 

        while time(9,30) <= datetime.now().time() <= time(16,00):
            tickrs_data_path=os.path.join(os.getcwd(),Config.DATA_PATH,"TICKRS.csv")
            tickrs_df=pd.read_csv(tickrs_data_path)
            if not tickrs_df.empty:
                # first update the symbol related information
                for tickr in tickrs_df.Tickrs.to_list():
                    self._l.update_existing_records(tickr)

                # perform backtest on those tickrs and display table
                __table = PrettyTable(['TICKR','DATE','RECOM','REASON','EMA5','SMA20','ADX_14','DMP_14','DMN_14','RSI','TSI','ACCURACY (%)','AVG DAYS'])
                for tickr in tickrs_df.Tickrs.to_list():
                    b=BackTest(tickr,-120,False,True)
                    __table.add_row(b.execute_strategy(True))
                print(__table)

                # sleep for 10 mns to avoid any threshold limit
                t.sleep(600)
        print("Market closed")

if __name__=='__main__':
    u=Updater()
    #u.load_data()
    u.perform_backtest()
    print("Performing update for the final time of the day")
    u.update_data()



