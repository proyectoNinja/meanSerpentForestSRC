import pandas as pd
import time
import datetime

print "Leyendo archivo..."
columnas=['Hora','Tipo','Historico','Leida']
data=pd.read_table('../csv.txt',header = 1, usecols=[1,2,3,4],names=columnas,parse_dates=True)
#data['Time']=data['Hora'].map(lambda x: pd.to_timeStamp()
#print data
#print data[(data['Hora']> '' )]
pd.groupby(data, by=[data['Hora']<'2016/04/9'])
pd.groupby(data, by=[data['Hora']>'2016/04/13 12:00'])
#data.groupby(pd.TimeGrouper(freq='H'))
print data
print "Hecho"
