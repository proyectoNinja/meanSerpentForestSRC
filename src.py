import pandas as pd
import numpy as np
import sys
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
        col=['Historico','Hora','Grupo']
        data=data[col]
        data=data.dropna(axis=0)
        data.set_index('Hora', inplace=True)
    elif (tipo==1):
        col=['Historico','Hora','Grupo']
        data=data[col]
        data=data.dropna(axis=0)
        data.set_index('Hora', inplace=True)
    elif (tipo==5):
        col=['Carbohidratos','Hora','Grupo']
        data=data[col]
        data=data.dropna(axis=0)
        data.set_index('Hora', inplace=True)
    elif (tipo==4):
        #data['InsulinaTiempo']=Rapida/lenta 1/0
        #data['InsulinaCantidad']=Int/NaN
        print 4
    return data

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

def parser(dir):
    columnas=['Hora','Tipo','Historico','Leida','Insulina rapida SV','Insulina rapida U','Alimentos SV','Carbohidratos','Insulina lenta SV']
    data=pd.read_table(dir,header=1,usecols=[1,2,3,4,5,6,7,8,9],names=columnas,parse_dates='Hora')
    format="%Y/%m/%d %H:%M"
    primeraHora = data['Hora'].min()
    data['Grupo']=data['Hora'].map(lambda x: clasificaPorHora(x,primeraHora,format))
    return data

if (len(sys.argv)==2):
    archivo=sys.argv[1]
else:
    archivo="../csv.txt"
    print "archivo ejemplo"
data=parser(archivo)
data=filtro(data,0)
data_agrupada=data.groupby('Grupo')
grupos=[]
for index,grupo in data_agrupada:
    grupo=grupo.drop('Grupo',axis=1)
    grupos.append(grupo)
print grupos[66]
grupos=np.array(grupos, dtype=object)
cluster=KMeans()
#cluster.fit(data)"""
print "Todo ha salido a pedir de boca"
