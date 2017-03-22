import pandas as pd
import numpy as np
import time
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
"""
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.cross_validation import KFold
from sklearn.cluster import KMeans as modulador
"""

def clasificaPorHora(hora,hMin,format):
    hClasificar=datetime.strptime(hora,format)
    hRef=datetime.strptime(hMin,format)
    grupo=0
    clasificado=False
    while(not clasificado):
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
data["date"] =data['Hora'].map(lambda x: pd.to_datetime(x,format=format, errors='ignore'))
data=data.drop('Hora', axis=1)
data=data.drop('Leida',axis=1)

historico=data.drop('Tipo',axis=1)
historico=historico.dropna(axis=0)
historico=historico.reindex()
data_historico=historico.groupby('Grupo')

print "Printing info..."
data0=data_historico.get_group(0).drop('Grupo',axis=1)
print data0

print "Ploting..."
data0.set_index('date', inplace=True)
plt.plot(data0)
plt.show()
"""
for i in range (90):
    plt.plot(historico.get_group(i))
    plt.show()

print "Preparando clusters"
modulador().fit(historico)
"""
print "Todo ha salido a pedir de boca"
