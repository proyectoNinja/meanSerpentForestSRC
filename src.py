import pandas as pd
import time
from datetime import datetime,timedelta

def clasificaPorHora(hora,hMin):
    format="%Y/%m/%d %H:%M"
    hClasificar=datetime.strptime(hora,format)
    hRef=datetime.strptime(hMin,format)
    grupo=0
    clasificado=False
    while(grupo<90 and not clasificado):
        horas=4*(grupo+1)
        if(hRef+timedelta(hours=horas)>hClasificar):
            clasificado=True
        else:
            grupo=grupo+1
        return grupo

#print "Leyendo archivo..."
#columnas=['Hora','Tipo','Historico','Leida']
#data=pd.read_table('../csv.txt',header = 1, usecols=[1,2,3,4],names=columnas,parse_dates=True)

#data['Time']=data['Hora'].map(lambda x: pd.to_timeStamp()
#print data
#print data[(data['Hora']> '' )]
#pd.groupby(data, by=[data['Hora']<'2016/04/9'])
#pd.groupby(data, by=[data['Hora']>'2016/04/13 12:00'])
#data.groupby(pd.TimeGrouper(freq='H'))
print clasificaPorHora("2016/03/30 16:44","2016/03/30 16:31")
print "Hecho"
