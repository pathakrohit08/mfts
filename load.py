import datetime
import io
import os
from datetime import datetime

import pandas as pd
import pandas_ta as ta

import config
from config import Config
from connection import SQLDB
from scraper import get_historic_data, get_live_data


class LoadTrade(object):
    """Use this class to update stock/asset and save it to the disk. 
    This could be done prior to the start of the market. You can use this 
    code to backtest your strategy"""

    def __init__(self):
        self.__dbconn=SQLDB()

    def add_new_records(self,tickr="",asset="",volume="",industry="",sector=""):
        self.__tickr=tickr
        self.__asset=asset
        self.__volume=volume
        self.__industry=industry
        self.__sector=sector

        df=self.__get_all_data(self.__tickr)
        df=self.__calculate_all_indicators(df)
        #self.process()
        #print(self.__df.tail(5))

        self.__insert_records(df,tickr)
        #self.__process_records(False)

    def __calculate_all_indicators(self,df):
        """use this function to calculate all the indicators value"""
        df=self.__calculate_moving_average(df)
        df=self.__calculate_tsi(df)
        df=self.__calculate_adx(df)
        df=self.__calculate_rsi(df)


        return df

    def __get_all_data(self,tickr):
        """use this function to populate the dataframe"""
        self.__csvurl=f"https://query1.finance.yahoo.com/v7/finance/download/{tickr}?period1=1092873600&period2={int(datetime.now().timestamp())}&interval=1d&events=history&includeAdjustedClose=true"
        s=get_historic_data(self.__csvurl)

        """you should not be able to access dataframe from outside the class"""
        df=pd.read_csv(io.StringIO(s.decode('utf-8')))
        print(df.head())
        df=df.dropna()
        df_columns=['Date','High','Low','Close','Adj Close']
        print(df.columns)
        if not set(df_columns).issubset(df.columns):
            raise ValueError(f"One or more columns are missing {df_columns}")

        if len(df.index)<5:
            raise ValueError(f"Cannot calculate EMA 5")

        if len(df.index)<20:
            raise ValueError(f"Cannot calculate SMA 20")

        """set date as index (required for filtering,sorting,grouping etc etc"""
        df['Date'] = pd.to_datetime(df['Date'], format = '%Y-%m-%d')

        df.set_index(['Date'], inplace=True)


        return df


    def update_existing_records(self,tickr=''):
        """use this function to update the records, offload it to celery in the future"""
        stock_master_df=self.__dbconn.get_tickr(tickr)

        if stock_master_df.empty:
            raise ValueError(f"data does not exist for {tickr}")

        last_updated_date=stock_master_df.iloc[0].LastUpdatedDate.strftime('%Y-%m-%d')
        print(f'Last updated date for {tickr},{last_updated_date}')
        current_date=datetime.now().strftime('%Y-%m-%d')

        if current_date!=last_updated_date and current_date>last_updated_date:
            df=self.__get_all_data(tickr)
            if not df.empty:
                mask = df.loc[last_updated_date:current_date, :]
                mask=mask.iloc[1:]
                if not mask.empty:
                    """we found records to be updated"""
                    self.__endDate=datetime(2012,5,12)
                    d1=self.__dbconn.get_stock_details(stock_master_df.iloc[0].Id,last_updated_date,self.__endDate.strftime("%Y-%m-%d"))
                    d1['Date'] = pd.to_datetime(d1['Date'], format = '%Y-%m-%d')
                    if d1.empty:
                        raise ValueError("Dataframe is empty")
                    #d1.set_index(['Date'], inplace=True)
                    result=pd.concat([d1,mask])
                    df=self.__calculate_all_indicators(result)
                    if not df.empty:
                        self.__dbconn.delete_stock_details(int(stock_master_df.iloc[0].Id))
                        df['stockId']=int(stock_master_df.iloc[0].Id)
                        self.__dbconn.save_data('stockdetails',df)

        sql = """ UPDATE public.stockmaster SET "LastUpdatedDate" = %s WHERE "Id" = %s"""
        self.__dbconn.update_stock_master(sql,current_date,int(stock_master_df.iloc[0].Id))
        print(f"Records updated for {tickr}")


    def __calculate_moving_average(self,df):
        """use this function to calculate moving averages for the asset
            1. If 5 EMA crosses 20 SMA its buy signal
            2. IS 20 SMA crosses 5 EMA its sell signal"""
        for m in Config.moving_average_conf:
            if m['type']=='simple':
                df[m['label']]=round(df[Config.PRICE_COL].rolling(window=m['days']).mean(),2)
            else:
                df[m['label']]=round(df[Config.PRICE_COL].ewm(span=m['days'], adjust=False).mean(),2)

        return df
            

    def __calculate_tsi(self,df):
        """user this function to calculate True strength index for the asset
            1. if TSI is positive its a buy signal
            2. if TSI is negative,time to sell
        read more here https://www.investopedia.com/terms/t/tsi.asp
        """
        df['TSI']=round(ta.tsi(df[Config.PRICE_COL]),2)
        df['TSI-C']=0


        return df
        
    def __calculate_rsi(self,df):
        """user this function to calculate RSI for the asset
            1. if TSI is positive its a buy signal
            2. if TSI is negative,time to sell
        read more here https://www.investopedia.com/terms/t/tsi.asp
        """
        df['RSI']=round(ta.rsi(df[Config.PRICE_COL]),2)

        return df
        
    def __calculate_adx(self,df):
        """use this function to calculate Average Directional Index.
            1. if DI+>DI- its a buy signal
            2. if DI+<DI- its a sell signal"""

        #print(df.head())
        adx_df=round(ta.adx(df['High'],df['Low'],df['Close']),2)
        #print(adx_df.tail())
        df=pd.concat([df,adx_df],axis=1)
        print("Succssfully merged")
        return df

    def __insert_records(self,df,tickr):
        stock_master_df=self.__dbconn.get_tickr(tickr)
        sql = """INSERT INTO public.stockmaster("Symbol","Name","Volume","Sector","Industry","LastUpdatedDate")
                VALUES(%s,%s,%s,%s,%s,%s) RETURNING "Id";"""
                
        stock_id=self.__dbconn.save_stock_master(sql,self.__tickr,
                self.__asset,self.__volume,
                self.__sector,self.__industry,datetime.now().strftime('%Y-%m-%d'))
        
        df['stockId']=stock_id
        #df['stockId']=stock_master_df.iloc[0].Id

        self.__dbconn.save_data('stockdetails',df)


   
            

            


    



