import math
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_ta as ta
import seaborn as sns

import config
import scraper
from config import Config
from connection import SQLDB
from scraper import get_historic_data, get_live_data

tickr='AMC'
price_col='Close'
positive=[]
total=[]
fig, ax = plt.subplots(4)
data_path=os.path.join(os.getcwd(),Config.DATA_PATH,tickr+'.csv')

df=pd.read_csv(data_path)
df['Date'] = pd.to_datetime(df['Date'], format = '%Y-%m-%d')
df.set_index(['Date'], inplace=True)

start_date = df.index[0]
end_date = df.index[-1]

after_start_date = df.index >= start_date
before_end_date = df.index <= end_date
between_two_dates = after_start_date & before_end_date
df = df.loc[between_two_dates]


def calculate_MA(days,type,label,col):
    """calculate moving averages"""
    df[label]=round(df[col].rolling(window=days).mean(),2) if type=='simple' else round(df[col].ewm(span=days, adjust=False).mean(),2)
    # df['SMA20'] = round(df[col].rolling(window=20).mean(),2)
    # df['SMA50'] = round(df[col].rolling(window=50).mean(),2)
    # df['EMA5'] = round(df[col].ewm(span=5, adjust=False).mean(),2)

for m in Config.moving_average_conf:
    calculate_MA(m['days'],m['type'],m['label'],price_col)



"""calculate TSI"""
df['TSI']=round(ta.tsi(df[price_col]),2)

"""calculate center line"""
df['TSI-C']=0



def calculate_TSI(days,label,col='TSI'):
    """ use this function to calculate tsi
        1. if TSI is positive its a buy signal
        2. if TSI is negative,time to sell
        read more here https://www.investopedia.com/terms/t/tsi.asp
        """
    df[label]=round(df[col].ewm(span=int(days), adjust=False).mean(),2)

for m in Config.tsi_conf:
    calculate_TSI(m['days'],m['label'],'TSI')

def plot_ma():
    ax[0].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, price_col], label=price_col,color='#71B1F8')
    ax[0].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'SMA20'], label = '20-days SMA',color='#E13D4B')
    # ax.plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'SMA50'], label = '50-days SMA',color='lime')
    ax[0].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'EMA5'], label = '5-days EMA',color='#00B061')
    ax[0].legend(loc='best')
    ax[0].set_ylabel('Price in $')
    ax[0].title.set_text('Moving average Graph')

def plot_tsi():
    ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI'], label='TSI',color='#71B1F8')
    #ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, '7-TSI'], label='7-TSI',color='#E13D4B')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-7'], label='7-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-8'], label='8-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-9'], label='9-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-10'], label='10-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-11'], label='11-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-12'], label='12-TSI')
    ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-C'], label='TSI-C',color='black')
    ax[1].title.set_text('TSI Graph')
    ax[1].set_ylabel('TSI value')
    ax[1].legend(loc='best')

def plot_rsi():
    ax[3].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'RSI'], label='RSI',color='#71B1F8')
    #ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, '7-TSI'], label='7-TSI',color='#E13D4B')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-7'], label='7-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-8'], label='8-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-9'], label='9-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-10'], label='10-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-11'], label='11-TSI')
    # ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'TSI-12'], label='12-TSI')
    ax[3].title.set_text('RSI Graph')
    ax[3].set_ylabel('RSI value')
    ax[3].legend(loc='best')

def plot_adx():
    ax[2].plot(adx_df.loc[start_date:end_date, :].index, adx_df.loc[start_date:end_date, 'ADX_14'], label='ADX (14)',color='#71B1F8')
    #ax[1].plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, '7-TSI'], label='7-TSI',color='#E13D4B')
    ax[2].plot(adx_df.loc[start_date:end_date, :].index, adx_df.loc[start_date:end_date, 'DMP_14'], label='DI+ (14)',color='green')
    ax[2].plot(adx_df.loc[start_date:end_date, :].index, adx_df.loc[start_date:end_date, 'DMN_14'], label='DI- (14)',color='red')
    ax[2].title.set_text('ADX Graph')
    ax[2].set_ylabel('ADX value')
    ax[2].legend(loc='best')



#print(df.columns)

"""calculate and plot ADX/DI+/DI-"""
adx_df=round(ta.adx(df['High'],df['Low'],df['Close']),2)
df['RSI']=round(ta.rsi(df['Close']))

df=pd.concat([df,adx_df],axis=1)
plot_ma()
plot_tsi()
plot_rsi()

plot_adx()


def plot_corelation():
    sns.set(color_codes=False, font_scale=1)
    df_cor = df[["Close", "Adj Close","Volume","EMA5","SMA20","TSI"]]
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


def check_buy_signal(row):
    # if row["EMA5"]>row["SMA20"]:
    #     print("EMA5 has crossed SMA20")
    # if row["TSI"]>0:
    #     print("TSI is above centerline")
    # if row["DMP_14"]>row["DMN_14"]:
    #     print("DI+ has crossed DI-")
    
    return row["EMA5"]>row["SMA20"] and row["TSI"]>0 and row["DMP_14"]>row["DMN_14"]

def get_buy_signal_reason(row):
    ans=[]
    if row["EMA5"]>row["SMA20"]:ans.append("EMA5 is greater than SMA20")
    if row["TSI"]>0:ans.append("TSI crossed centerline")
    if row["DMP_14"]>row["DMN_14"]:ans.append("DI+ is above DI-")

    return ans

def check_sell_signal(row):
    return row["EMA5"]<row["SMA20"] or row["TSI"]<0 or row["DMP_14"]<row["DMN_14"] or row["ADX_14"]>row["DMP_14"]

def get_sell_signal_reason(row):
    if row["EMA5"]<row["SMA20"]: return "EMA5 went below SMA20"
    if row["TSI"]<0:return "TSI is below center line"
    if row["DMP_14"]<row["DMN_14"]:return "DI+ went under DI-"
    if row["ADX_14"]>row["DMP_14"]: return "ADX14 went above DI, indicates overbought"
    #     
    # if row["TSI"]<0:
    #     print("TSI is below centerline")
    # if row["DMP_14"]<row["DMN_14"]:
    #     print("DI+ has sunk below DI-")


def record_strategy(change,start_date,end_date):
    if change>=0:
        positive.append((change,start_date.strftime("%A %d. %B %Y"),end_date.strftime("%A %d. %B %Y")))
    total.append((change,start_date.strftime("%A %d. %B %Y"),end_date.strftime("%A %d. %B %Y")))
    

def calculate_accuracy():
    if len(positive)>0:
        return round(len(positive)/len(total)*100,2)
    else:
        return 0

#plt.show()
print(df.columns)
#print(df.tail())
stock_buy_date=''
stock_sell_date=''
active_strategy=False
start_amount=0
invested_amount=0
for index, row in df.iterrows():
    if active_strategy:
        if check_sell_signal(row):
            print(f"Exiting from strategy --> sell signal received,{get_sell_signal_reason(row)}")

            print(f'Initial value: {round(start_amount,2)}$, Final value: {round(invested_amount,2)}$, change: {round(invested_amount-start_amount,2)}$, stock buy date: {stock_buy_date.strftime("%A %d. %B %Y")}, stock_sell_date: {last_day.strftime("%A %d. %B %Y")}')
            active_strategy=False
            record_strategy(round(invested_amount-start_amount,2),stock_buy_date,last_day)
        else:
            new_price=row['Close']
            new_investment_amount=invested_amount+(new_price-last_price)
            percent_diff = ((new_investment_amount - invested_amount)/invested_amount) * 100
            if percent_diff<-10:
                stock_sell_date=index
                print(f"we entered a stop loss {percent_diff}")
                if check_sell_signal(row): #Do you also want to check if sell signal is generated
                    print(f'Initial value: {round(start_amount,2)}$, Final value: {round(new_investment_amount,2)}$, change: {round(new_investment_amount-start_amount,2)}$, stock buy date: {stock_buy_date.strftime("%A %d. %B %Y")}, stock_sell_date: {last_day.strftime("%A %d. %B %Y")}')
                    print("Exiting from strategy --> stop loss hit")
                    active_strategy=False
                    record_strategy(round(new_investment_amount-start_amount,2),stock_buy_date,last_day)
                #print(round(new_price,2),round(last_price,2),round(new_investment_amount,2),round(invested_amount,2),round(percent_diff,2),index)
            print(f'${round(start_amount,2)} ,${round(new_investment_amount,2)}, ${round(new_investment_amount-start_amount,2)},{index.strftime("%A %d. %B %Y")}')
            invested_amount=new_investment_amount
            #time.sleep(1)
            

    else:
        if check_buy_signal(row):
            ans=get_buy_signal_reason(row)
            d=index.strftime("%A %d. %B %Y")
            print(f"Entering into  strategy {d},{ans}")
            active_strategy=True
            stock_buy_date=index
            start_amount=row['Close']
            invested_amount=row['Close']
        

    last_price=row['Close']
    last_day=index

if active_strategy:
    print(f'${round(new_investment_amount-start_amount,2)},{last_day}')
    
print(f"Total accuracy of the model is {calculate_accuracy()} %")
#print(sorted(positive,key=lambda x:x[0],reverse=True)[0:10])
#print(sorted(total,key=lambda x:x[0],reverse=True)[0:10])
#print(df.tail(50))
plt.show()
