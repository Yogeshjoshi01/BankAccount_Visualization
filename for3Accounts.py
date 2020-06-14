# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:23:32 2020

@author: yoges
"""

import pandas as pd
import requests
import os
from zipfile import ZipFile
from datetime import datetime,date
import matplotlib.pyplot as plt
import calendar
import matplotlib.ticker as mtick

#Getting url 
url = "https://www.dropbox.com/s/ib6s7wmvcj2ujgl/554625.csv?dl=1"

#GET requests to the url
vizObj = requests.get(url)

#Check if it was loaded sucessfully
vizObj.status_code

#Get the content into a zip folder
#with open("vizObj.zip","wb") as f:
#    f.write(vizObj.content)
#   
#getting the contents of he zip folder into another directory
#with ZipFile("vizObj.zip","r") as zipObj:
#    zipObj.extractall()
#
#delete the file
#os.remove("vizObj.zip")
    
#required whenworking offline
with open("bankAcctsForViz.csv","wb") as f:
    f.write(vizObj.content)
    

#reading all three csv files
start = pd.read_csv("startBalance.csv")
bankAcct=pd.read_csv("bankAcctsForViz.csv")
transData=pd.read_csv("bankTransactions.csv")

#merging the two files
mergestartTransData = pd.merge(start,transData,how="outer",on="bankAcctID",suffixes=("_left","_right"))
mergeAll = pd.merge(bankAcct,mergestartTransData,how="left",on="bankAcctID")

#Appending the TOP ROW
for i in mergeAll["bankAcctID"].unique():
    for j in range(len(mergeAll)):
        if i == mergeAll.loc[j,"bankAcctID"]:
            mergeAll=mergeAll.append({"bankAcctID":mergeAll.iloc[j,0],"date_right":mergeAll.iloc[j,3],"transAmount":mergeAll.iloc[j,2]},ignore_index=True)
            break
        
#Sorting and grouping values
mergeAll = mergeAll.sort_values(by = ['bankAcctID','date_right','transAmount'],ascending = [True,True,False])
mergeAll = mergeAll.set_index([pd.Index(range(len(mergeAll)))])
mergeAll = mergeAll.groupby(["bankAcctID","date_right"])
mergeAll2 = pd.DataFrame(columns=["transAmount","MaxAmount"])
mergeAll2["transAmount"] = mergeAll.transAmount.sum()
mergeAll2["MaxAmount"] = mergeAll.transAmount.max()

for i in range(len(mergeAll2["MaxAmount"].values)):
    if mergeAll2.iloc[i,1] < mergeAll2.iloc[i,0]:
        mergeAll2.iloc[i,1] = mergeAll2.iloc[i,0]
        

#Creating anpther dataframe so that grouped values and indexes can be pasted into it
mergeAll1 = pd.DataFrame(columns = ["bankAcctID","date_right","transAmount1","MaxAmount"])
mergeAll1["transAmount1"]=mergeAll2["transAmount"].values
mergeAll1["MaxAmount"] = mergeAll2["MaxAmount"].values
mergeAll1["bankAcctID"] = mergeAll2.index.get_level_values(0)
mergeAll1["date_right"] = mergeAll2.index.get_level_values(1)

#inserting a new column
mergeAll1.insert(4,"cumAmt",0)
mergeAll1.cumAmt = mergeAll1.cumAmt.astype(float)

#set the index
for j in mergeAll1.bankAcctID.unique():
    flag = 0
    for i in (mergeAll1[mergeAll1["bankAcctID"]==j].index):
        if flag == 0:
            mergeAll1.cumAmt[i] = mergeAll1.transAmount1[i]
        else:
            mergeAll1.cumAmt[i] = mergeAll1.cumAmt[i-1] + mergeAll1.transAmount1[i]
        flag+=1
        
#converting to datetime object
mergeAll1["date_right"] = mergeAll1["date_right"].astype("datetime64[ns]")

#Getting day of week in numbers and then converting to days of week
mergeAll1['day_of_week'] = mergeAll1['date_right'].dt.dayofweek
days = {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'}

#using lamdbda and apply inbuilt functions of python
mergeAll1['day_of_week'] = mergeAll1['day_of_week'].apply(lambda x: days[x])

#Filtering dataframe
mergeAll1 = mergeAll1[mergeAll1["date_right"]>="2020-03-01"]

#Setting the index of the dataframe
mergeAll1 = mergeAll1.set_index([pd.Index(range(len(mergeAll1.transAmount1)))])

#Filtering for Values greater than $200
mergeAll1["transAmount2"] = list(x if x> 200 else 0 for x in mergeAll1["MaxAmount"])

#mergeAll1.to_csv("mergeAll1.csv",index=False)
#mergeAll.to_csv("mergeAll.csv",index=False)

#------------------DO NOT MAKE ANY CHANGES ABOVE THIS --------------------------

#CREATING FIGURE AND AXES OBJECT
ax1 = []
fig = plt.figure(figsize=(8,20))
ax1.append(fig.add_subplot(4,1,1))
ax1.append(fig.add_subplot(4,1,2))
ax1.append(fig.add_subplot(4,1,3,sharex=ax1[1],sharey=ax1[1]))
ax1.append(fig.add_subplot(4,1,4,sharex=ax1[2],sharey=ax1[2]))

#CREATING A COLOR OBJECT 
color = ['tab:green','tab:orange','tab:purple']

#PLOTTING LINE PLOT AND BAR PLOT WITHIN SUBPLOTS
flag = 1
flag1 = 0
for j in mergeAll1["bankAcctID"].unique():
    x=mergeAll1["date_right"][mergeAll1["bankAcctID"]==j]
    y=mergeAll1["cumAmt"][mergeAll1["bankAcctID"]==j]
    ax1[0].plot(x,y,drawstyle ="steps-post",linewidth=1,label="EOD Acct Balance",color = color[flag1])
    x1 = mergeAll1["date_right"][mergeAll1["bankAcctID"]==j]
    y1 = mergeAll1["transAmount2"][mergeAll1["bankAcctID"]==j]
    ax1[flag].bar(x1,y1,color = color[flag1])
    ax1[flag].grid(True)
    ax1[flag].set_xticks(["2020-03-01", "2020-03-15", "2020-04-01","2020-04-15","2020-05-1"])
    ax1[flag].set_xticklabels(["March 01", "March 15", "April 01", "April 15","May 01"])
    flag+=1
    flag1+=1

#SETTING TITLE AND LABEL FOR BOTTOM THREE SUBPLOTS
flag = 1   
for j in mergeAll1["bankAcctID"].unique():
    ax1[flag].set_title("Acct. Number: "+str(j))
    ax1[flag].set_ylabel("Total Daily Deposits")
    ax1[flag].text("2020-03-15", -70, 'Showing ONLY Total Deposits Over $ 200',fontsize=10)
    flag+=1
ax1[0].grid(True)

#SETTING YMIN., TICKS FOR Y AXIS
ax1[0].set_ylim(ymin=0)
fmt = '${x:,.0f}'
tick = mtick.StrMethodFormatter(fmt)
ax1[0].yaxis.set_major_formatter(tick)
ax1[1].set_ylim(ymin=-100)
fmt = '${x:,.0f}'
tick = mtick.StrMethodFormatter(fmt)
ax1[1].yaxis.set_major_formatter(tick)    
ax1[0].set_xticks(["2020-03-01", "2020-03-15", "2020-04-01","2020-04-15","2020-05-1"])
ax1[0].set_xticklabels(["March 01", "March 15", "April 01", "April 15","May 01"])
ax1[0].legend(labels=mergeAll1["bankAcctID"].unique(),loc='lower right')
ax1[0].set_title("EOD Acct Balance (Yogesh' version)")

#CREATING ANNONATIONS OVER BAR PLOTS
flag = 1
for j in mergeAll1["bankAcctID"].unique():
    for i in mergeAll1[mergeAll1["bankAcctID"]==j].index:
        if mergeAll1.loc[i,"transAmount2"] > 200.00:
            text1 = ax1[flag].annotate(int(round(mergeAll1.loc[i,"transAmount2"])),xy=(mergeAll1.loc[i,"date_right"],mergeAll1.loc[i,"transAmount2"]+10))
            text2 = ax1[flag].annotate(mergeAll1.loc[i,"day_of_week"]+"\n"+str(mergeAll1.loc[i,"date_right"].month)+"/"+str(mergeAll1.loc[i,"date_right"].day),xy=(mergeAll1.loc[i,"date_right"],mergeAll1.loc[i,"transAmount2"]+70))
            text1.set_fontsize(7)
            text2.set_fontsize(7)
    flag += 1

#SAVING FIGURE
fig.savefig("554625.pdf")