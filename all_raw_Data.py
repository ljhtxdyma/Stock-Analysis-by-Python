# -*- coding: utf-8 -*-
# author:Liu Jiahui

import pandas as pd
from datetime import datetime, date
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import numpy as np
import tushare as ts
import csv


# part1: define a function where get data from Yahoo finance

def get_data(code,origin):
    finalresult=None
    try:
        if origin=='SH':
            origin='SS'
        data = web.DataReader(code+'.'+origin,"yahoo",datetime(2009,1,1),date.today())
        
        if len(data.index.tolist())>5:
            data.to_csv(str(code)+'.'+str(origin)+"_result.csv",encoding='utf_8_sig')
                 
    except:
        pass
    else:
        pass
    return finalresult

# part2: get all the code info from web
pro = ts.pro_api('3e3ed9ba576210c210d0aa08959fdd3b32de36515af178850f05e151')
data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
data.to_csv("all_code_data.csv",encoding='utf_8_sig')

data.dropna(axis=0,how='any',inplace=True)

data.drop(['symbol','name','area','list_date'],axis=1,inplace=True)

for i in data['ts_code']:
    code=str(i)[0:6]
    origin=str(i)[7:9]
    get_data(code,origin)

print('done!')
    







    
