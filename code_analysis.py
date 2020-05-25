# -*- coding: utf-8 -*-
# author:Liu Jiahui

import pandas as pd
from datetime import datetime, date
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import tkinter as tk
import numpy as np
import tushare as ts
import csv
from pylab import mpl
from threading import Thread

mpl.rcParams['font.sans-serif'] = ['SimHei']    # 指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False      


pro = ts.pro_api('3e3ed9ba576210c210d0aa08959fdd3b32de36515af178850f05e151')
rawdata = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
rawdata.to_csv("all_code_data.csv",encoding='utf_8_sig')

rawdata.dropna(axis=0,how='any',inplace=True)

rawdata.drop(['symbol','name','area','list_date'],axis=1,inplace=True)

all_close_one_year = pd.DataFrame({'weekday':['Monday', 'Tuesday','Wednesday','Thursday','Friday']})
all_close_one_year .set_index('weekday',inplace=True)
all_close_half_year = pd.DataFrame({'weekday':['Monday', 'Tuesday','Wednesday','Thursday','Friday']})
all_close_half_year .set_index('weekday',inplace=True)
all_close_three_months = pd.DataFrame({'weekday':['Monday', 'Tuesday','Wednesday','Thursday','Friday']})
all_close_three_months .set_index('weekday',inplace=True)

def get_data(code_name,days):
    finalresult=None

    try:
        all_data=pd.read_csv(str(code_name)+"_result.csv",encoding='utf_8_sig')
        
        
        
        if len(all_data.index.tolist())>days:
            data=all_data.tail(days)
            data.set_index('Date',inplace=True)
            index=[]

            for i in range(data.shape[0]):
                index.append(i)
                
            data['Index']=index
            data['Date']=data.index
            data.set_index('Index',inplace=True)
            data.dropna(axis=0,how='any')
            lyzz=data.loc[:,['Date','Close']]

            j=0

            for i in lyzz['Date']:
                weekday=datetime.strptime(str(i),'%Y-%m-%d').weekday()
                if weekday==0:
                    lyzz.loc[[j],['Date']]='Monday'
                elif weekday==1:
                    lyzz.loc[[j],['Date']]='Tuesday'
                elif weekday==2:
                    lyzz.loc[[j],['Date']]='Wednesday'
                elif weekday==3:
                    lyzz.loc[[j],['Date']]='Thursday'
                else:
                    lyzz.loc[[j],['Date']]='Friday'
                    
                j=j+1

            stock_date=lyzz['Date'].values.tolist()
            stock_close=lyzz['Close'].values.tolist()
            stock_close_balance=[]


            for i in range(len(stock_close)-1):
                if stock_close[i+1]-stock_close[i]>=0:
                    stock_close_balance.append(1)
                else:
                    stock_close_balance.append(0)
                i=i+1
                

            stock_date.pop(0)


            newdata={'weekday':stock_date,'close_balance':stock_close_balance}

            newframe=pd.DataFrame(newdata)

            finalframe=pd.pivot_table(newframe,index=[u'weekday'])

            finalresult=finalframe.loc[['Monday', 'Tuesday','Wednesday','Thursday','Friday'], :]
            finalresult.rename(columns={'close_balance':str(code_name)},inplace=True)
    except:
        pass
    else:
        pass
    return finalresult


if __name__=="__main__":
    
    for i in rawdata['ts_code']:

        all_close_one_year=pd.concat([all_close_one_year,get_data(str(i),260)],axis=1)
        all_close_half_year=pd.concat([all_close_half_year,get_data(str(i),130)],axis=1)
        all_close_three_months=pd.concat([all_close_three_months,get_data(str(i),65)],axis=1)

            
    all_close_one_year.to_csv("all_close_one_year.csv",encoding='utf_8_sig')

    all_close_half_year.to_csv("all_close_half_year.csv",encoding='utf_8_sig')
        
    all_close_three_months.to_csv("all_close_three_months.csv",encoding='utf_8_sig')   


    
