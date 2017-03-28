import pandas as pd
import numpy as np
import time
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

"""
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.cross_validation import KFold
"""

def filtro(data,tipo):
    if (tipo==0):
        historico=data.drop('Leida',axis=1)
        historico=historico.drop('Tipo',axis=1)
        historico=historico.dropna(axis=0)
        final=historico.reindex()
        final.set_index('Hora', inplace=True)
    elif (tipo==1):
        leida=data.drop('Historico',axis=1)
        leida=leida.drop('Tipo',axis=1)
        leida=leida.dropna(axis=0)
        final=leida.reindex()
        final.set_index('Hora', inplace=True)
    return final

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

def printAndPlotGroup(data,tipo,grupo):
    imprimir=filtro(data.get_group(grupo),tipo)
    imprimir=imprimir.drop('Grupo',axis=1)
    print imprimir
    imprimir.plot()
    plt.show()

print "Leyendo archivo..."
columnas=['Hora','Tipo','Historico','Leida']
data=pd.read_table('../csv.txt',header = 1, usecols=[1,2,3,4],names=columnas,parse_dates='Hora')

print "Realizando adaptaciones pertinentes..."
print "Esto puede tardar unos segundos"
format="%Y/%m/%d %H:%M"
data['Grupo']=data['Hora'].map(lambda x: clasificaPorHora(x,"2016/03/30 16:30",format))
#data=filtro(data,0)
data_agrupada=data.groupby('Grupo')
printAndPlotGroup(data_agrupada,0,0)
#asd=KMeans()
asd.fit(data_agrupada)


print "Todo ha salido a pedir de boca"
