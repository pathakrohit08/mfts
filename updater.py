from __future__ import absolute_import

import argparse
import datetime
import io
import os
import time as t
from datetime import datetime, time, timedelta

import pandas as pd
from prettytable import PrettyTable

from backtest import BackTest
from config import Config
from connection import SQLDB
from load import LoadTrade
from scraper import get_live_data
from utilities import send_email
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


class Updater:
    def __init__(self):
        self.master_df=None
        self._l=LoadTrade()
        data_path=os.path.join(os.getcwd(),Config.DATA_PATH,"holidays.csv")
        self.holidays_df=pd.read_csv(data_path)

    def load_data(self,filename='nasdaq.csv'):
        """use this function to seed the database"""
        data_path=os.path.join(os.getcwd(),Config.DATA_PATH,filename)
        self.master_df=pd.read_csv(data_path)
        send_email("starting initial seeding of data","Load Data")
        for index,row in self.master_df.iterrows():
            try:
                if row["Symbol"] in ['TSLA']:
                    print(f'processing {row["Symbol"]},{row["Name"]}')
                    self._l.add_new_records(row['Symbol'],row['Name'],row['Volume'],row['Industry'],row['Sector'])
                    # intentionally sleep to avoid any threshold limit
                    t.sleep(2)
            except Exception as e:
                print(f"Exception occured during seeding the database {e}")

        send_email("Initial load of data was complete","Load Data")

    def update_data(self,filename='nasdaq.csv'):
        """use this function to update the data"""
        send_email('Starting daily update of the data','Update Data')
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

        send_email("Daily update of the data was complete","Update Data",f"{datetime.now().strftime('%Y-%m-%d')}-report.log")


    def perform_backtest(self):
        """use this function to perform backtest"""
        current_date=datetime.now().strftime('%m-%d-%Y') 
        if  current_date in self.holidays_df.Date.to_list() or datetime.today().isoweekday()== 6 or datetime.today().isoweekday()== 7:
            print("Market is closed for today")
            return

        while time(9,00) <= datetime.now().time() <= time(16,00):
            tickrs_data_path=os.path.join(os.getcwd(),Config.DATA_PATH,"TICKRS.csv")
            tickrs_df=pd.read_csv(tickrs_data_path)
            tickrs_to_ignore=set()
            if not tickrs_df.empty:
                # first update the symbol related information
                for tickr in tickrs_df.Tickrs.to_list():
                    try:
                        self._l.update_existing_records(tickr)
                    except Exception as e:
                        tickrs_to_ignore.add(tickr)
                        print(f"Error while updating data for {tickr}-->{e}")

                # perform backtest on those tickrs and display table
                __table = PrettyTable(['TICKR','DATE','RECOM','REASON','CLOSE','EMA5','SMA20','ADX_14','DMP_14','DMN_14','RSI','TSI','ACCURACY (%)','AVG DAYS'])
                for tickr in tickrs_df.Tickrs.to_list():
                    if tickr not in tickrs_to_ignore:
                        b=BackTest(tickr,-120,False,True)
                        __table.add_row(b.execute_strategy(False))
                print(__table)
                print(f"Next update at {datetime.now() + timedelta(seconds = 300)}")

                # sleep for 10 mns to avoid any threshold limit
                t.sleep(300)
        print("Market closed")


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('m')
    args = parser.parse_args()
    u=Updater()
    if args.m=="backtest":
        u.perform_backtest()
    elif args.m=="update":
        u.update_data()
    elif args.m=="load":
        u.load_data()

    
    #u=Updater()
    #u.load_data()
    #u.perform_backtest()
    #u.update_data()



