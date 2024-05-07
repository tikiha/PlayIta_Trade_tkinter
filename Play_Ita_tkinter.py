#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tkinter as tk
from tkinter import ttk

from pandas_datareader import data
import re

import time
import datetime

import sqlite3
import csv
import requests
import pandas as pd


# In[2]:


# 変数代入
speed=1000
job=None
ttid_list_Sell=(0,1,2,3,4,5)
ttid_list_Buy=(0,1,2,3,4,5)
ttid_current=0
pprice=0


# In[3]:


# 再生button呼び出し
def Saisei(event=None):
    if job is not None:
        root.after_cancel(job)
    Build_ita()
    Time_select()
    Update_ita()
    tree.yview(ttid_current-10)


# In[4]:


# 銘柄呼び出し
def Symbol(event=None):
    
    for i in symbol_tree.get_children():
        symbol_tree.delete(i)
    
    conn = sqlite3.connect("./Record/23"+entry_day.get()+"/"+"am.db")
    c=conn.cursor()
    query='''select symbol_code, symbol_name from symbol'''
    c.execute(query)
    symbol=c.fetchall()

    for m in symbol:
        k=(m[0],m[1])
        symbol_tree.insert(parent='',index='end',values=k)


# In[5]:


def Speed_1():
    global speed
    speed=1000

def Speed_2():
    global speed
    speed=500

def Speed_10():
    global speed
    speed=100


# In[6]:


# ウィジェット作成
root=tk.Tk()
root.geometry("700x500")
root.title("板プレイヤー")


# In[7]:


# frame_entry作成
column=(1,2,3)

frame_entry=tk.LabelFrame(root, pady=10, padx=10)
frame_entry.pack(side=tk.LEFT, fill=tk.Y)
label_day=tk.Label(frame_entry,text='日付')
label_day.grid(column=0,row=0)
entry_day=tk.Entry(frame_entry)
entry_day.grid(column=1,row=0)

button_symbol=tk.Button(frame_entry,text='銘柄検索',command=Symbol)
button_symbol.grid(column=1,row=1)

label_symbol=tk.Label(frame_entry,text='銘柄')
label_symbol.grid(column=0,row=2)
symbol_tree=ttk.Treeview(frame_entry,columns=(1,2),height=10,show='headings')
symbol_tree.grid(column=1,row=2)
symbol_tree.column(1,anchor='center',width=50)
symbol_tree.column(2,anchor='center',width=80)
symbol_tree.heading(1,text='code')
symbol_tree.heading(2,text='name')



label_time=tk.Label(frame_entry,text='時間')
label_time.grid(column=0,row=3)
entry_time=tk.Entry(frame_entry)
entry_time.grid(column=1,row=3)

button_play=tk.Button(frame_entry,text='再生',command=Saisei)
button_play.grid(column=1,row=4)

button_1speed=tk.Button(frame_entry,text='１倍速',command=Speed_1)
button_1speed.grid(column=0,row=5)
button_2speed=tk.Button(frame_entry,text='２倍速',command=Speed_2)
button_2speed.grid(column=0,row=6)
button_10speed=tk.Button(frame_entry,text='１０倍速',command=Speed_10)
button_10speed.grid(column=0,row=7)

entry_day.bind("<Return>", Symbol)
entry_time.bind("<Return>",Saisei)


# In[8]:


# tick_frame_tree作成
tick_frame_tree=tk.Frame(root,relief=tk.RAISED)
tick_frame_tree.pack(side=tk.LEFT)
tick_tree_scroll=tk.Scrollbar(tick_frame_tree)
tick_tree_scroll.pack(side=tk.RIGHT,fill=tk.Y)
tick_tree=ttk.Treeview(tick_frame_tree,columns=column,height=20,show='headings',yscrollcommand=tick_tree_scroll.set)
tick_tree_scroll.config(command=tick_tree.yview)
tick_tree.pack()

tick_tree.column(1,anchor='center',width=50)
tick_tree.column(2,anchor='center',width=50)
tick_tree.column(3,anchor='center',width=50)
tick_tree.heading(1,text='時刻')
tick_tree.heading(2,text='値段')
tick_tree.heading(3,text='株数')


# In[9]:


# frame_tree作成

frame_tree=tk.Frame(root, pady=10, padx=10,relief=tk.RAISED)
frame_tree.pack(side=tk.LEFT)
tree_scroll=tk.Scrollbar(frame_tree)
tree_scroll.pack(side=tk.RIGHT,fill=tk.Y)
tree=ttk.Treeview(frame_tree,columns=column,height=20,show='headings',yscrollcommand=tree_scroll.set)
tree.pack()

tree_scroll.config(command=tree.yview)
tree.column(1,anchor='center',width=80)
tree.column(2,anchor='center',width=80)
tree.column(3,anchor='center',width=80)


# In[10]:


# 指定のDBから情報取得
def DB_Info():
    
    t=int(entry_time.get())
    if t<113100:
        t='am'
    else:
        t='pm'
    conn = sqlite3.connect("./Record/23"+entry_day.get()+"/"+t+".db")
    c=conn.cursor()
    
    record_id = symbol_tree.focus()
    a =symbol_tree.item(record_id, 'values')[0]

    query='''select * from stream_data
            where content_symbol=='''+str(a)
    
    c.execute(query)
    result=c.fetchall()
    
    return result


# In[11]:


# 指定のcsvから情報取得
def Tick_csv_import():
    day=entry_day.get()
    record_id = symbol_tree.focus()
    code =symbol_tree.item(record_id, 'values')[0]    
    df=pd.read_csv(r"C:\Users\yskhj\Downloads\Trade\ita_record\23"+day+"\qr-"+code+"-2023"+day+".csv", encoding='utf-8')
    df_i=df.set_index('時刻')
    df_i=df_i.iloc[::-1]
    return df_i


# In[12]:


# 時間指定
def Time_select():
    
    global n
    
    result=DB_Info()
    result=pd.DataFrame(result)
    result_i=result.set_index(1)
    
    a=entry_time.get()
    b=a[0]+a[1]+':'+a[2]+a[3]+':'+a[4]+a[5]
    
    n=result_i.index.get_loc(b)


# In[13]:


def Min_Max(yes_P):
    if yes_P<100:
        max_min=(-30,31,1)
    elif 100<=yes_P<200:
        min_max=(-50,51,1)
    elif 200<=yes_P<500:
        min_max=(-80,81,1)
    elif 500<=yes_P<700:
        min_max=(-100,101,1)
    elif 700<=yes_P<1000:
        min_max=(-150,151,1)
    elif 1000<=yes_P<1500:
        min_max=(-300,301,1)
    elif 1500<=yes_P<2000:
        min_max=(-400,401,1)
    elif 2000<=yes_P<3000:
        min_max=(-500,501,1)
    elif 3000<=yes_P<5000:
        min_max=(-700,701,5)
    elif 5000<=yes_P<7000:
        min_max=(-1000,1001,10)
    elif 7000<=yes_P<10000:
        min_max=(-1500,1501,10)
    else:
        min_max=(-3000,3001,10)
    
    return min_max


# In[14]:


# 板基礎作り
def Build_ita():
    
    global yes_P
    global min_max
    
    for i in tree.get_children():
        tree.delete(i)
    
    conn = sqlite3.connect("./Record/23"+entry_day.get()+"/am.db")
    c=conn.cursor()
    record_id = symbol_tree.focus()
    a =symbol_tree.item(record_id, 'values')[0]
    yes_P='''select yes_price from symbol where symbol_code=='''+str(a)
    c.execute(yes_P)
    yes_P=c.fetchone()[0]
    min_max=Min_Max(yes_P)
        
    for m in range (min_max[0],min_max[1],min_max[2]):
        k=('',yes_P+m,'')
        tree.insert(parent='',index='0',values=k,tags=min_max[1]-1-m)


# In[15]:


def update_column(result,n):
    tree.heading(1,text=result[n][3])
    tree.heading(2,text=result[n][1])
    tree.heading(3,text=result[n][4])


# In[16]:


def tag_return(tid):
    tree.tag_configure(tid, background="")


# In[17]:


def Update_ita():
    
    global n
    global ttid_list_Sell
    global ttid_list_Buy
    global ttid_current
    global job
    global pprice
    
    tid_list_Sell=[]
    tid_list_Buy=[]
    result=DB_Info()
    
    # Current
    if result[n][5] is not None:
        tid_current=int(min_max[1]-1-result[n][5]+yes_P)
        tree.tag_configure(ttid_current,foreground="")
        tree.tag_configure(tid_current,foreground="red")
        ttid_current=tid_current

    
    # Sell
    for i in range (6,11):
        tid=int(min_max[1]-1-result[n][i+10]+yes_P)
        tid_list_Sell.append(tid)
        
        target=tree.get_children()[int(tid/min_max[2])]
        temp=tree.item(target,'values')
        
        try:
            t=int(temp[0])
        except:
            t=0
        
        # 数量変更
        if t != result[n][i]:
            temp=(result[n][i],result[n][i+10],'')
            tree.item(target,values=temp)
            tree.tag_configure(tid, background="yellow")
            tree.after(300,tag_return,tid)
            
    # １秒前の気配値でなくなった値を削除
    for i in range (0,5):    
        price_change=ttid_list_Sell[i] in tid_list_Sell
        if price_change==False:
            target=tree.get_children()[int(ttid_list_Sell[i]/min_max[2])]
            temp=tree.item(target,'values')
            temp=('',temp[1],temp[2])
            tree.item(target,values=temp)

    # Buy
    for i in range (11,16):
        tid=int(min_max[1]-1-result[n][i+10]+yes_P)
        tid_list_Buy.append(tid)
        target=tree.get_children()[int(tid/min_max[2])]
        temp=tree.item(target,'values')
        
        try:
            t=int(temp[2])
        except:
            t=0
            
        if t!=result[n][i]:
            temp=(temp[0],result[n][i+10],result[n][i])
            tree.item(target,values=temp)
            tree.tag_configure(tid, background="yellow")
            tree.after(300,tag_return,tid)
            
    for i in range (0,5):
        price_change=ttid_list_Buy[i] in tid_list_Buy
        if price_change==False:
            target=tree.get_children()[int(ttid_list_Buy[i]/min_max[2])]
            temp=tree.item(target,'values')
            temp=(temp[0],temp[1],'')
            tree.item(target,values=temp)
    
    ttid_list_Sell=tid_list_Sell 
    ttid_list_Buy=tid_list_Buy
    
    update_column(result,n)
    Update_ayumi(result,n)
    
    n+=1
    
    job=root.after(speed,Update_ita)


# In[18]:


def Update_ayumi(result,n):
    global pprice
    try:
        df_i=Tick_csv_import()
    
    except:
        pass
    
    try:
        tf=df_i.loc[result[n][1]]
        if (type(tf) is pd.core.frame.DataFrame):
            for a in range(len(tf.axes[0])):
                price=tf.iat[a,0]
                volume=tf.iat[a,1]
                k=(result[n][1],price,volume)
                color=str(n)+str(a)
                tick_tree.insert(parent='',index='0',values=k,tags=color)
                if price>pprice:
                    tick_tree.tag_configure(color,foreground='red')
                if price<pprice:
                    tick_tree.tag_configure(color,foreground='blue')
                    
                pprice=price

                
        else:
            color=str(n)
            price=tf[0]
            k=(result[n][1],tf[0],tf[1])
            tick_tree.insert(parent='',index='0',values=k,tags=color)
            if price>pprice:
                tick_tree.tag_configure(color,foreground='red')
            if price<pprice:
                tick_tree.tag_configure(color,foreground='blue')
            pprice=price
        
        
    except:
        KeyError


# In[19]:


root.mainloop()

