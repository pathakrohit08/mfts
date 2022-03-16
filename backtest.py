"""Use this class to backtest your strategy"""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import config
from config import Config
from connection import SQLDB


class BackTest(object):
    def __init__(self,tickr,days,plot_graph=False,verbose=False):
        self.__tickr=tickr
        self.__startDate=datetime.now()
        #self.__endDate=datetime.now()+timedelta(days=days)
        self.__endDate=datetime(2012,5,12)
        self.__dbconn=SQLDB()
        self.__df=self.__load_data()
        self.__df['Date'] = pd.to_datetime(self.__df['Date'], format = '%Y-%m-%d')
        self.__df.set_index(['Date'], inplace=True)
        if plot_graph:self.__plot()
        self.positive=[]
        self.total=[]
        self.trading_days=[]
        #print(f'Accuracy for {self.__tickr} strategy is {self.calculate_accuracy()}%')

    def __load_data(self):
        stock_master_df=self.__dbconn.get_tickr(self.__tickr)
        if stock_master_df.empty:
            raise ValueError(f"data does not exist for {self.__tickr}")

        return self.__dbconn.get_stock_details(stock_master_df.iloc[0].Id,self.__startDate.strftime("%Y-%m-%d"),self.__endDate.strftime("%Y-%m-%d"))

    def __plot(self):
        """use this function to plot datapoints for better visualization"""

        fig, ax = plt.subplots(4)
        start_date=self.__df.index[0]
        end_date=self.__df.index[-1]
        def plot_ma():
            """Internal function to plot moving averages"""
            ax[0].plot(self.__df.loc[start_date:end_date, :].index, self.__df.loc[start_date:end_date, Config.PRICE_COL], label=Config.PRICE_COL,color='#71B1F8')
            ax[0].plot(self.__df.loc[start_date:end_date, :].index, self.__df.loc[start_date:end_date, 'SMA20'], label = '20-days SMA',color='#E13D4B')# ax.plot(df.loc[self.__startDate:self.__endDate, :].index, df.loc[self.__startDate:self.__endDate, 'SMA50'], label = '50-days SMA',color='lime')
            ax[0].plot(self.__df.loc[start_date:end_date, :].index, self.__df.loc[start_date:end_date, 'EMA5'], label = '5-days EMA',color='#00B061')
            ax[0].legend(loc='best')
            ax[0].set_ylabel('Price in $')
            ax[0].title.set_text('Moving average Graph')


        def plot_tsi():
            """Internal function to plot True strength index"""
            ax[1].plot(self.__df.loc[start_date:end_date, :].index, self.__df.loc[start_date:end_date, 'TSI'], label='TSI',color='#71B1F8')
            ax[1].plot(self.__df.loc[start_date:end_date, :].index, self.__df.loc[start_date:end_date, 'TSI-C'], label='TSI-C',color='black')
            ax[1].title.set_text('TSI Graph')
            ax[1].set_ylabel('TSI value')
            ax[1].legend(loc='best')

        def plot_adx():
            """Internal function to plot ADX"""
            ax[2].plot(self.__df.loc[start_date:end_date, :].index, self.__df.loc[start_date:end_date, 'ADX_14'], label='ADX (14)',color='#71B1F8')
            #ax[1].plot(df.loc[self.__startDate:self.__endDate, :].index, df.loc[self.__startDate:self.__endDate, '7-TSI'], label='7-TSI',color='#E13D4B')
            ax[2].plot(self.__df.loc[start_date:end_date, :].index, self.__df.loc[start_date:end_date, 'DMP_14'], label='DI+ (14)',color='green')
            ax[2].plot(self.__df.loc[start_date:end_date :].index, self.__df.loc[start_date:end_date, 'DMN_14'], label='DI- (14)',color='red')
            ax[2].title.set_text('ADX Graph')
            ax[2].set_ylabel('ADX value')
            ax[2].legend(loc='best')

        def plot_rsi():
            """Internal function to plot ADX"""
            ax[3].plot(self.__df.loc[start_date:end_date, :].index, self.__df.loc[start_date:end_date, 'RSI'], label='RSI',color='#71B1F8')
            #ax[1].plot(df.loc[self.__startDate:self.__endDate, :].index, df.loc[self.__startDate:self.__endDate, '7-TSI'], label='7-TSI',color='#E13D4B')
            ax[3].title.set_text('RSI Graph')
            ax[3].set_ylabel('RSI value')
            ax[3].legend(loc='best')


        def plot_corelation():
            """Internal function to plot corelation matrix"""
            sns.set(color_codes=False, font_scale=1)
            df_cor = self.__df[["Close", "Adj Close","Volume","EMA5","SMA20","TSI"]]
            corr = df_cor.corr()

            # Generate a mask for the upper triangle
            mask = np.triu(np.ones_like(corr, dtype=bool))

            # Set up the matplotlib figure
            f, ax = plt.subplots(figsize=(11, 9))

            # Generate a custom diverging colormap
            cmap = sns.diverging_palette(230, 20, as_cmap=True)

            # Draw the heatmap with the mask and correct aspect ratio
            sns.heatmap(corr, mask=mask,cmap= 'coolwarm', vmax=.3, center=0,annot=False,
                    square=True, linewidths=.5, cbar_kws={"shrink": .5})

        plot_ma()
        plot_tsi()
        plot_adx()
        plot_rsi()
        plot_corelation()

        plt.show()

    def __check_buy_signal(self,row):
        return row["EMA5"]>row["SMA20"] and row["TSI"]>0 and row["DMP_14"]>row["DMN_14"] and row["Close"]>row["SMA20"]

    def __get_buy_signal_reason(self,row):
        ans=[]
        if row["EMA5"]>row["SMA20"]:ans.append("EMA5 > SMA20")
        if row["TSI"]>0:ans.append("TSI>0")
        if row["DMP_14"]>row["DMN_14"]:ans.append("DI+ > DI-")

        return ans

    def __check_sell_signal(self,row):
        #return row["EMA5"]<row["SMA20"] or row["TSI"]<0 or row["DMP_14"]<row["DMN_14"] or row["ADX_14"]>row["DMP_14"] or row['RSI']>=70
        return  row["Close"]<row["SMA20"] or row["EMA5"]<row["SMA20"] or row["TSI"]<0 or row["DMP_14"]<row["DMN_14"] or row['RSI']>=80

    def __get_sell_signal_reason(self,row):
        if row["EMA5"]<row["SMA20"]: return "EMA5 < SMA20"
        if row["TSI"]<0:return "TSI < 0"
        if row["DMP_14"]<row["DMN_14"]:return "DI+ < DI-"
        if row["RSI"]>80: return "RSI > 80"
        if row["Close"]<row["SMA20"]: return "Close price down"

    def record_strategy(self,change,start_date,end_date):
        if change>=0:
            self.trading_days.append((end_date-start_date).days)
            self.positive.append((change,start_date.strftime("%A %d. %B %Y"),end_date.strftime("%A %d. %B %Y")))
        self.total.append((change,start_date.strftime("%A %d. %B %Y"),end_date.strftime("%A %d. %B %Y")))
    

    def calculate_accuracy(self):
        if len(self.positive)>0:
            return round(len(self.positive)/len(self.total)*100,2)
        else:
            return 0

    def execute_strategy(self,verbose=False):
        #print(self.__df.tail())
        stock_buy_date=''
        stock_sell_date=''
        active_strategy=False
        start_amount=0
        last_price=0
        invested_amount=0
        last_day=None
        for index, row in self.__df.iterrows():
            if active_strategy:
                if self.__check_sell_signal(row):
                    if verbose:
                        print(f"Exiting from strategy --> sell signal received,{self.__get_sell_signal_reason(row)}")
                        print(f'Initial value: {round(start_amount,2)}$, Final value: {round(invested_amount,2)}$, change: {round(invested_amount-start_amount,2)}$, stock buy date: {stock_buy_date.strftime("%A %d. %B %Y")}, stock_sell_date: {last_day.strftime("%A %d. %B %Y")}')
                    active_strategy=False
                    self.record_strategy(round(invested_amount-start_amount,2),stock_buy_date,last_day)
                else:
                    new_investment_amount=invested_amount+(row['Close']-last_price)
                    percent_diff = ((new_investment_amount - invested_amount)/invested_amount) * 100
                    if percent_diff<-10:
                        stock_sell_date=index
                        if verbose:
                            print(f"we entered a stop loss {percent_diff}")
                        if self.__check_sell_signal(row): #Do you also want to check if sell signal is generated
                            if verbose:
                                print(f'Initial value: {round(start_amount,2)}$, Final value: {round(new_investment_amount,2)}$, change: {round(new_investment_amount-start_amount,2)}$, stock buy date: {stock_buy_date.strftime("%A %d. %B %Y")}, stock_sell_date: {last_day.strftime("%A %d. %B %Y")}')
                                print("Exiting from strategy --> stop loss hit")
                            active_strategy=False
                            self.record_strategy(round(new_investment_amount-start_amount,2),stock_buy_date,last_day)
                    if verbose:
                        print(f'${round(start_amount,2)} ,${round(new_investment_amount,2)}, ${round(new_investment_amount-start_amount,2)},{index.strftime("%A %d. %B %Y")}')
                    invested_amount=new_investment_amount
            else:
                if self.__check_buy_signal(row):
                    ans=self.__get_buy_signal_reason(row)
                    d=index.strftime("%A %d. %B %Y")
                    if verbose:
                        print(f"Entering into  strategy {d},{ans}")
                    active_strategy=True
                    stock_buy_date=index
                    start_amount=row['Close']
                    invested_amount=row['Close']
            

            last_price=row['Close']
            last_day=index


        if active_strategy:
            return [self.__tickr, index.strftime('%Y-%m-%d'),"YES" ,"All",round(row['Close'],2),row['EMA5'],row['SMA20'],row['ADX_14'],row['DMP_14'],row['DMN_14'],row['RSI'],row['TSI'],self.calculate_accuracy(),sum(self.trading_days)//len(self.trading_days)]
        else:
            return [self.__tickr, index.strftime('%Y-%m-%d'),"NO" ,self.__get_sell_signal_reason(row),round(row['Close'],2),row['EMA5'],row['SMA20'],row['ADX_14'],row['DMP_14'],row['DMN_14'],row['RSI'],row['TSI'],self.calculate_accuracy(),sum(self.trading_days)//len(self.trading_days)]


    



    
