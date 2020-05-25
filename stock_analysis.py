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

# part1: define a function getting data from Yahoo finance

def get_data(code,origin):
    finalresult=None
    try:
        if origin=='SH':
            origin='SS'
        data = web.DataReader(code+'.'+origin,"yahoo",datetime(2009,1,1),date.today())
        
        if len(data.index.tolist())>5:
            index=[]

            for i in range(data.shape[0]):
                index.append(i)
                
            data['Index']=index
            data['Date']=data.index
            data.set_index('Index',inplace=True)
            data.dropna(axis=0,how='any')
            lyzz=data.loc[:,['Date','Open','Close']]

            j=0

            for i in lyzz['Date']:
                weekday=datetime.strptime(str(i),'%Y-%m-%d %H:%M:%S').weekday()
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
            stock_open=lyzz['Open'].values.tolist()
            stock_close=lyzz['Close'].values.tolist()
            stock_open_balance=[]
            stock_close_balance=[]


            for i in range(len(stock_close)-1):
                if stock_close[i+1]-stock_close[i]>=0:
                    stock_close_balance.append(1)
                else:
                    stock_close_balance.append(0)
                i=i+1
                
            for i in range(len(stock_open)-1):
                if stock_open[i+1]-stock_close[i]>=0:
                    stock_open_balance.append(1)
                else:
                    stock_open_balance.append(0)
                i=i+1

            stock_date.pop(0)


            newdata={'weekday':stock_date,'open_balance':stock_open_balance,'close_balance':stock_close_balance}

            newframe=pd.DataFrame(newdata)

            finalframe=pd.pivot_table(newframe,index=[u'weekday'])

            finalresult=finalframe.loc[['Monday', 'Tuesday','Wednesday','Thursday','Friday'], :]
            finalresult['weekday']=finalresult.index
            s=pd.Series([code]*5)
            finalresult.set_index([s],inplace=True)
    except:
        pass
    else:
        pass
    return finalresult

# part2: get all the code info from web

def store_data():
    pro = ts.pro_api('3e3ed9ba576210c210d0aa08959fdd3b32de36515af178850f05e151')
    data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    data.to_csv("all_code_data.csv",encoding='utf_8_sig')

    data.dropna(axis=0,how='any',inplace=True)

    data.drop(['symbol','name','area','list_date'],axis=1,inplace=True)

    def store_type_data(type_name, type_data):
        final_result = pd.DataFrame(columns=['close_balance', 'open_balance', 'weekday'])
        
        for i in type_data['ts_code']:
            code=str(i)[0:6]
            origin=str(i)[7:9]
            result=get_data(code,origin)
            if result is not None:
                final_result=pd.concat([final_result,result])
        final_result.to_csv(str(type_name)+"_result.csv",encoding='utf_8_sig')
        print(str(type_name)+' done!')
        
    i=0
    tsk = []
    
    for type_name, type_data in data.groupby("industry"):
        print(str(i)+'start')
        th=Thread(target=store_type_data,args=[type_name, type_data,])
        th.start()
        tsk.append(th)
        i=i+1
        
    for th in tsk:
        th.join()



#part3: analyze data and plot the chart

if __name__=="__main__":

    
    store_data()

    data=pd.read_csv("all_code_data.csv",encoding='utf_8_sig')

    data.dropna(axis=0,how='any',inplace=True)

    data.drop(['symbol','name','area','list_date'],axis=1,inplace=True)

    type_list=data["industry"].unique().tolist()

    all_open_balance = pd.DataFrame({'weekday':['Monday', 'Tuesday','Wednesday','Thursday','Friday']})
    all_open_balance.set_index('weekday',inplace=True)
    all_close_balance = pd.DataFrame({'weekday':['Monday', 'Tuesday','Wednesday','Thursday','Friday']})
    all_close_balance.set_index('weekday',inplace=True)

    for i in type_list:
        type_data = pd.read_csv(str(i)+"_result.csv",encoding='utf_8_sig')
        type_data.drop(['Unnamed: 0'],axis=1,inplace=True)

        finalframe=pd.pivot_table(type_data,index=[u'weekday'])
        finalresult=finalframe.loc[['Monday', 'Tuesday','Wednesday','Thursday','Friday'], :]
        finalresult.rename(columns={'open_balance':str(i)+'_open_balance'},inplace=True)
        finalresult.rename(columns={'close_balance':str(i)+'_close_balance'},inplace=True)
        open_balance=finalresult[str(i)+'_open_balance']
        close_balance=finalresult[str(i)+'_close_balance']

        all_open_balance=pd.concat([all_open_balance,open_balance],axis=1)
        all_close_balance=pd.concat([all_close_balance,close_balance],axis=1)


    all_open_balance.to_csv("all_open_balance.csv",encoding='utf_8_sig')
    all_close_balance.to_csv("all_close_balance.csv",encoding='utf_8_sig')

    all_close_delta=all_close_balance.max()-all_close_balance.min()

    analysis_result=pd.concat([all_close_balance.max(),all_close_balance.min(),all_close_delta],axis=1)
    analysis_result.rename(columns={0: "max", 1:"min", 2: "delta"},inplace=True)
    analysis_result.sort_values("delta",inplace=True)

    head=analysis_result.head(20)
    tail=analysis_result.tail(20)

    type_name_tail=tail.index.tolist()
    type_name_head=head.index.tolist()
    type_name_tail.reverse()

    x=['周一','周二','周三','周四','周五']


    def autolabel(rects):
         for rect in rects:  
                height = rect.get_height()
                plt.text(rect.get_x()+rect.get_width()/2.-0.2, 1.03*height, '%.2f%%' % (height * 100),fontsize=8)

    def plotchart(type_list,name):
        fig=plt.figure(figsize=(16, 16))
        j=1
        for k in type_list:
            i=str(k)[0:-14]
            y = all_close_balance[k].tolist()
            delta=max(y)-min(y)
            ax = fig.add_subplot(4, 5, j)
            plt.xticks(np.arange(len(x)),x)
            a=plt.bar(np.arange(len(x)),y,width=0.5,color='b')
            plt.title(i)
            ax.set_ylabel('涨跌概率')
            autolabel(a) 
            plt.ylim((0.3,0.7))
            #plt.legend(handles=[],labels=('%.2f%%' % (delta*100)),loc='upper right',fancybox=True, framealpha=0.1)
            plt.plot([], [], ' ', label=('概率差值：'+'%.2f%%' % (delta*100)))
            plt.legend(loc='upper right',fancybox=False, framealpha=0,fontsize=8)
            j=j+1

        fig.tight_layout(pad=3, w_pad=3.0, h_pad=5.0)

        plt.savefig(name+'.png')

    plotchart(type_name_tail,'前20')
    plotchart(type_name_head,'后20')
        
    plt.show()


    


'''
# part4: UI design
code=None
origin=None
date_Start=None
date_End=None


window = tk.Tk()
window.title('Stock Analysis Demo Version')
window.geometry('500x300')

var = tk.StringVar()
l = tk.Label(window, text=var, bg='white', font=('Arial', 12), width=30, height=2)
l.pack()

canvas = tk.Canvas(window, bg='green', height=200, width=500)

b = tk.Button(window, text="hit me", command=get_data())


image_file = tk.PhotoImage(file='123.jpg')
image = canvas.create_image(200, 0, anchor='n', image=image_file)

canvas.pack(side='top')

e1 = tk.Entry(window, show=None, font=('Arial', 14))
e1.pack

window.mainloop()

'''










