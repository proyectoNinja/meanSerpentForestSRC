import pandas as pd
import numpy as np
import sys
import time
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

"""imports RandomForest
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import GroupKFold
    from sklearn.cross_validation import KFold
"""

def filtro(data,tipo):
    if (tipo==0):
        col=['Historico','Hora','Grupo']
        data=data[col]
        data=data.dropna(axis=0)
    elif (tipo==1):
        col=['Leida','Hora','Grupo']
        data=data[col]
        data=data.dropna(axis=0)
    """tipos 4 y 5
        elif (tipo==4):#
            data['Carbohidratos']=data['Alimentos SV'].map(lambda comida: estimador(comida,data))
        elif (tipo==5 or tipo==4):
        #Carbohidratos
            if (tipo==5):
                col=['Carbohidratos','Hora','Grupo']
                data=data[col]
                data=data.dropna(axis=0)
                data['Ingesta']=1
            if (tipo==4):
                if (data['Alimentos SV']):
                    print 6
            #elif (tipo==4):
            #data['InsulinaTiempo']=Rapida/lenta 1/0
            #data['InsulinaCantidad']=Int/NaN
    """
    format="%Y/%m/%d %H:%M"
    data['Indice']=data['Hora'].map(lambda hora: int(time.mktime(datetime.strptime(hora,format).timetuple())))
    data=data.drop('Hora',axis=1)
    data.set_index('Indice', inplace=True)
    return data

def estimador(comida,data):
    if (comida>0):
        return data['Carbohidratos'].median()
    else:
        return 0

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
    return int(grupo)

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


if (len(sys.argv)>1):
    archivo=sys.argv[1]
else:
    archivo="../csv.txt"
    print "archivo ejemplo"
data=parser(archivo)
data=filtro(data,0)
data_agrupada=data.groupby('Grupo')
"""drop de 'grupo' y clustering
    Esto deberia dropear la columa grupos pero no lo hace
    for index,grupo in data_agrupada:
        grupo=grupo.drop('Grupo',axis=1)
        print index
        print grupo
    print data_agrupada.get_group(82)
    cluster=KMeans()
    cluster.fit(data_agrupada)
"""
print "Todo ha salido a pedir de boca"
