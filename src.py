import pandas as pd
import numpy as np
import time
from datetime import datetime,timedelta

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold

def clasificaPorHora(hora,hMin,format):
    hClasificar=datetime.strptime(hora,format)
    hRef=datetime.strptime(hMin,format)
    grupo=0
    clasificado=False
    while(grupo<89 and not clasificado):
        horas=4*(grupo+1)
        if(hRef+timedelta(hours=horas)>hClasificar):
            clasificado=True
        else:
            grupo=grupo+1
    return grupo

print "Leyendo archivo..."
columnas=['Hora','Tipo','Historico','Leida']
data=pd.read_table('../csv.txt',header = 1, usecols=[1,2,3,4],names=columnas,parse_dates=True)

print "Realizando adaptaciones pertinentes..."
format="%Y/%m/%d %H:%M"
data['Grupo']=data['Hora'].map(lambda x: clasificaPorHora(x,"2016/03/30 16:30",format))
data["date"]=data['Hora'].map(lambda x: pd.to_datetime(x,format=format, errors='ignore'))
data=data.drop('Hora',axis=1)
data_grupada=data.groupby(by="Grupo")
predictors=["Tipo","date"]
target=["Historico","Leida"]

print "Preparando IA..."
gkf = GroupKFold(n_splits=3)

print "Hecho"
