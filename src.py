import pandas as pd
import numpy as np
import sys
import time
import timeit
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

valorMinimo=8
_nClusters=8

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
    #data['Indice']=data['Hora'].map(lambda hora: int(time.mktime(datetime.strptime(hora,format).timetuple())))
    #data=data.drop('Hora',axis=1)
    data.set_index('Hora', inplace=True)
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
    return int(grupo)

def printAndPlotGroup(data,grupo):
    imprimir=data.get_group(grupo).drop('Grupo',axis=1)
    print imprimir
    imprimir.plot()
    plt.show()

def parser(dir):
    start = timeit.timeit()
    columnas=['Hora','Tipo','Historico','Leida','Insulina rapida SV',
    'Insulina rapida U','Alimentos SV','Carbohidratos','Insulina lenta SV']
    data=pd.read_table(dir,header=1,usecols=[1,2,3,4,5,6,7,8,9],
    names=columnas,parse_dates='Hora')
    format="%Y/%m/%d %H:%M"
    end = timeit.timeit()
    print "tiempo neto de read"
    print end - start
    primeraHora = data['Hora'].min()
    data['Grupo']=data['Hora'].map(lambda x: clasificaPorHora(x,primeraHora,format))
    print "tiempo neto de conversion"
    print end - timeit.timeit()
    return data

def cribador(data):
    contadorDeApariciones = data['Grupo'].value_counts(sort=False)
    grupo=0
    for a in contadorDeApariciones:#esto es muy ineficiente
        if (a!=16 or a<valorMinimo):
            data=data[data.Grupo!=grupo]
        elif(a>=valorMinimo and a<16):
            rowsNeeded=16-a
        grupo=grupo+1
    #print data.describe()
    return data


def procesado(data):
    data=cribador(data)
    data_final=data.groupby('Grupo')
    data_agrupada=[]
    for index,grupo in data_final:
        data_agrupada.append(grupo['Historico'])
        #data_tratable=data.drop(values=index,axis=0)
    clustering=KMeans(n_clusters=_nClusters)
    clustering.fit(data_agrupada)
    #data['Cluster']=data.['grupo'].map(lambda x: clustering.labels_[x])

    clusters=[]
    for i in range(_nClusters):
        clusters.append([])
    for i,j in zip(clustering.labels_,data_agrupada):
        clusters[i].append(j)
    for i in range(_nClusters):
        for group in clusters[i]:
            plt.plot(group)
        plt.axis([])
        plt.show()


def main():
    if (len(sys.argv)>1):
        archivo=sys.argv[1]
    else:
        archivo="../csv.txt"
    data=parser(archivo)
    data=filtro(data,0)
    procesado(data)

main()
