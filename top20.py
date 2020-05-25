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

all_close_one_year=pd.read_csv("all_close_one_year.csv",encoding='utf_8_sig')
all_close_one_year.set_index('weekday',inplace=True)
all_close_half_year=pd.read_csv("all_close_half_year.csv",encoding='utf_8_sig')
all_close_half_year.set_index('weekday',inplace=True)       
all_close_three_months=pd.read_csv("all_close_three_months.csv",encoding='utf_8_sig')
all_close_three_months.set_index('weekday',inplace=True)

def plot_code_chart(all_close_balance,name):
    all_close_delta=all_close_balance.max()-all_close_balance.min()

    analysis_result=pd.concat([all_close_balance.max(),all_close_balance.min(),all_close_delta],axis=1)
    analysis_result.rename(columns={0: "max", 1:"min", 2: "delta"},inplace=True)
    analysis_result.sort_values("delta",inplace=True)

    tail=analysis_result.tail(20)

    type_name_tail=tail.index.tolist()
    type_name_tail.reverse()

    x=['周一','周二','周三','周四','周五']


    def autolabel(rects):
         for rect in rects:  
                height = rect.get_height()
                plt.text(rect.get_x()+rect.get_width()/2.-0.2, 1.03*height, '%.2f%%' % (height * 100),fontsize=8)

    fig=plt.figure(figsize=(16, 16))
    j=1
    for k in type_name_tail:
        i=str(k)
        y = all_close_balance[k].tolist()
        delta=max(y)-min(y)
        ax = fig.add_subplot(4, 5, j)
        plt.xticks(np.arange(len(x)),x)
        a=plt.bar(np.arange(len(x)),y,width=0.5,color='b')
        plt.title(i)
        ax.set_ylabel('涨跌概率')
        autolabel(a) 
        plt.ylim((0,1))
        #plt.legend(handles=[],labels=('%.2f%%' % (delta*100)),loc='upper right',fancybox=True, framealpha=0.1)
        plt.plot([], [], ' ', label=('概率差值：'+'%.2f%%' % (delta*100)))
        plt.legend(loc='upper right',fancybox=False, framealpha=0,fontsize=8)
        j=j+1

    fig.tight_layout(pad=3, w_pad=3.0, h_pad=5.0)

    plt.savefig(name+'.png')


plot_code_chart(all_close_one_year,'一年前20')
plot_code_chart(all_close_half_year,'半年前20')
plot_code_chart(all_close_three_months,'三个月前20')





