import pandas as pd
import numpy as np
import sys
import time
import timeit
import math
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabaz_score, silhouette_samples


valorMinimo=8
_nClusters=8
nombreDatos= [  'Glucosa Media', 'Desviacion tipica','Glucosa maxima media',
                'Glucosa minima media','Porcentaje de tiempo en rango 70-180',
                'Numero medio de eventos por debajo del minimo(60)',
                'Numero medio de eventos por encima del maximo (240)',
                'Maximo numero de eventos fuera de rango(60-240)',
                'Minimo numero de eventos fuera de rango(60-240)']

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
    columnas=['Hora','Tipo','Historico','Leida','Insulina rapida SV',
    'Insulina rapida U','Alimentos SV','Carbohidratos','Insulina lenta SV']
    data=pd.read_table(dir,header=1,usecols=[1,2,3,4,5,6,7,8,9],
    names=columnas,parse_dates='Hora')
    format="%Y/%m/%d %H:%M"
    primeraHora = data['Hora'].min()
    data['Grupo']=data['Hora'].map(lambda x: clasificaPorHora(x,primeraHora,format))
    return data

def eleccion(data_valores, data_trabajo):
    for n_clusters in range(_nClusters-1):
        clusterer = KMeans(n_clusters=n_clusters+2, random_state=10)
        cluster_labels = clusterer.fit_predict(data_trabajo)
        silhouette_avg = silhouette_score(data_valores, cluster_labels)
        cal_score = calinski_harabaz_score(data_valores,cluster_labels)
        print("For n_clusters =", n_clusters+2,
              "The average silhouette_score is :", silhouette_avg,
              ", the calinski_harabaz score is ", cal_score,)

def procesado(data):
    data_final=data.groupby('Grupo')
    data_agrupada=[]
    data_pendiente=[]
    for index,grupo in data_final:
        if(len(grupo['Historico'])==16):
            data_agrupada.append(grupo['Historico'])
            data_pendiente.append(grupo.Pendiente)
    eleccion(data_agrupada,data_pendiente)
    #exit()
    clustering=KMeans(n_clusters=_nClusters)
    clustering.fit(data_pendiente)
    clusters=[]
    datos=[]
    for i in range(_nClusters):
        clusters.append([])
        datos.append([])
        for j in range(9):
            datos[i].append([])
    for i,j in zip(clustering.labels_,data_agrupada):
        clusters[i].append(j)
    for i in range(_nClusters):
        sumaDeMedias=0
        sumaDeMaximos=0
        sumaDeMinimos=0
        sumaDeEventosBajos=0
        sumaDeEventosAltos=0
        nSegmentos=0
        n=0
        glucosaMinMedia=sys.maxint
        glucosaMaxMedia=0
        varianza=0
        nVecesEnRango=0
        nMinDeEventosMalos=16
        sumaDeEventosMalosGrupo=0
        for group in clusters[i]:
            sumaDeMedias+=group.mean()
            sumaDeMaximos+=group.max()
            sumaDeMinimos+=group.min()
            nSegmentos+=1
            nMaxDeEventosMalos=0
            plt.subplot(2,4,i+1)
            plt.plot(group)
            plt.axis([0,15,40,350])
            for registro in group:
                varianza+=registro*registro
                n+=1
                if (registro>=70 and registro<=180):
                    nVecesEnRango+=1
                elif (registro<=60):
                    sumaDeEventosBajos+=1
                    sumaDeEventosMalosGrupo+=1
                elif (registro>=240):
                    sumaDeEventosAltos+=1
                    sumaDeEventosMalosGrupo+=1
            if(sumaDeEventosMalosGrupo>nMaxDeEventosMalos):
                nMaxDeEventosMalos=sumaDeEventosMalosGrupo
            elif(sumaDeEventosMalosGrupo<nMinDeEventosMalos):
                nMinDeEventosMalos=sumaDeEventosMalosGrupo
        varianza=varianza/n-(n+1*n+1)
        datos[i][0]=sumaDeMedias/nSegmentos #media
        datos[i][1]=math.sqrt(varianza) #Desviacion estandar
        datos[i][2]=sumaDeMaximos/nSegmentos #media de maximos
        datos[i][3]=sumaDeMinimos/nSegmentos #media de minimos
        datos[i][4]=float(nVecesEnRango)/n*100 #% de tiempo en rango
        datos[i][5]=float(sumaDeEventosBajos)/n #media de eventos bajos <60
        datos[i][6]=float(sumaDeEventosAltos)/n #media de eventos altos >240
        datos[i][7]=nMaxDeEventosMalos #maximo de eventos malos en un mismo segmento
        datos[i][8]=nMinDeEventosMalos #minimo de eventos malos en un mismo segmento
    for cluster in range(8):
        print datos[cluster]
    plt.show()

def main():
    if (len(sys.argv)>1):
        archivo=sys.argv[1]
    else:
        archivo="../csv.txt"
    data=parser(archivo)
    data=filtro(data,0)
    calculaPendiente(data)
    procesado(data)

def calculaPendiente(data):
    anterior=data['Historico'].mean()
    pendiente=[]
    for his in data['Historico']:
        pendiente.append(his-anterior)
        anterior=his
    data['Pendiente']=pendiente
main()
