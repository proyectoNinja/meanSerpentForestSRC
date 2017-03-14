import pandas as pd
import time
import datetime

def clasificaPorHora(hora,hMin):
    grupo=0
    clasificado=False
    while(grupo<90&&!clasificado):
        horas=4*(grupo+1)
        if(hora+timedelta(hours=horas)>hora):
            clasificado=True
        else:
            grupo=grupo+1
        return grupo
        
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
