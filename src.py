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
import hdbscan

valorMinimo=8
_nClusters=5
nombreDatos= [  'Glucosa Media', 'Desviacion tipica','Glucosa maxima media',
                'Glucosa minima media','Porcentaje de tiempo en rango 70-180',
                'Numero medio de eventos por debajo del minimo(60)',
                'Numero medio de eventos por encima del maximo (240)',
                'Maximo numero de eventos fuera de rango(60-240)',
                'Minimo numero de eventos fuera de rango(60-240)']

def getRegistros0(data):
    data=filtro(data,0)
    return data

def filtro(data,tipo):
    if (tipo==0):
        col=['Historico','Hora','Grupo']
        data=data[col]
        data=data.dropna(axis=0)
    elif (tipo==1):
        col=['Leida','Hora','Grupo']
        data=data[col]
        data=data.dropna(axis=0)
    format="%Y/%m/%d %H:%M"
    data.set_index('Hora', inplace=True)
    return data

def get_group(hora,hMin,format):
    group = 0
    hora_Actual=datetime.strptime(hora,format)
    hora_minima=datetime.strptime(hMin,format)

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
    names=columnas)
    format="%Y/%m/%d %H:%M"
    primeraHora = data['Hora'].min()
    data['Hora'].map(lambda x: get_group(x,primeraHora,format))
    data['Grupo']=data['Hora'].map(lambda x: clasificaPorHora(x,primeraHora,format))
    return data

def infoKMeans(data_trabajo, data_valores):
    for n_clusters in range(16):
        clusterer = KMeans(n_clusters=n_clusters+2, random_state=10)
        cluster_labels = clusterer.fit_predict(data_trabajo)
        silhouette_avg = silhouette_score(data_valores, cluster_labels)
        cal_score = calinski_harabaz_score(data_valores,cluster_labels)
        print("For n_clusters =", n_clusters+2,
              "The average silhouette_score is :", silhouette_avg,
              ", the calinski_harabaz score is ", cal_score,)

def rellenaUnSoloHueco(data):
    contadorFila=0
    contadorGrupo=0
    grupoActual=0
    valorAnterior=data['Historico'].head()
    horaGuardada=data.head(n=1).index
    print str(horaGuardada)
    for hora,valor,grupo in zip(data.index,data['Historico'],data['Grupo']):
        contadorGrupo+=1
        if (contadorGrupo==17):
            grupoActual+=1
            contadorGrupo=1
        if(hora+17-horaGuardada>0 and hora+17-horaGuardada<10):
            print "introducimos nuevo valor en ", hora+15
            data[index+15]=[(valor+valorAnterior)/2,grupo]
            contadorGrupo+=1
        horaGuardada=hora
        valorAnterior=valor
    return data

def getInfo(clusters):
    datos=[]
    for i in range(len(clusters)):
        datos.append([])
        for j in range(9):
            datos[i].append([])
    for i in range(len(clusters)):
        sumaDeMedias=0
        sumaDeMaximos=0
        sumaDeMinimos=0
        sumaDeEventosBajos=0
        sumaDeEventosAltos=0
        nSegmentos=0
        n=0
        glucosaMinMedia=sys.maxint
        glucosaMaxMedia=0
        nVecesEnRango=0
        nMinDeEventosMalos=16
        sumaDeEventosMalosGrupo=0
        for group in clusters[i]:
            sumaDeMedias+=group.mean()
            sumaDeMaximos+=group.max()
            sumaDeMinimos+=group.min()
            nSegmentos+=1
            nMaxDeEventosMalos=0
            for registro in group:
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
        datos[i][0]=sumaDeMedias/nSegmentos #media
        datos[i][2]=sumaDeMaximos/nSegmentos #media de maximos
        datos[i][3]=sumaDeMinimos/nSegmentos #media de minimos
        datos[i][4]=float(nVecesEnRango)/n*100 #% de tiempo en rango
        datos[i][5]=float(sumaDeEventosBajos)/n #media de eventos bajos <60
        datos[i][6]=float(sumaDeEventosAltos)/n #media de eventos altos >240
        datos[i][7]=nMaxDeEventosMalos #maximo de eventos malos en un mismo segmento
        datos[i][8]=nMinDeEventosMalos #minimo de eventos malos en un mismo segmento
        varianza=0
        n=0
        for group in clusters[i]:
            for registro in group:
                varianza+=(registro-datos[i][0]) ** 2
                n+=1
        varianza=varianza/n
        datos[i][1]=math.sqrt(varianza) #Desviacion estandar
    return datos

def getPlot(clusters):
    tam=int(math.sqrt(len(clusters)))+1
    for i in range(len(clusters)):
        for group in clusters[i]:
            plt.subplot(tam,tam,i+1)
            plt.plot(group)
            plt.axis([0,15,40,350])
    return plt

def KMeansClustering(data,nclusters):
    clustering=KMeans(n_clusters=nclusters)
    clustering.fit(data)
    clusters=[]
    for i in range(_nClusters):
        clusters.append([])
    for i,j in zip(clustering.labels_,data):
        clusters[i].append(j)
    return clusters

def HDBSCANclustering(data):
    clusterer = hdbscan.HDBSCAN(metric='manhattan',min_cluster_size=2, min_samples=2)
    clusterer.fit(data)
    _nClusters=clusterer.labels_.max()
    silhouette_avg = silhouette_score(data, clusterer.labels_)
    cal_score = calinski_harabaz_score(data,clusterer.labels_)
    print("For n_clusters =", _nClusters,
      "The average silhouette_score is :", silhouette_avg,
      ", the calinski_harabaz score is ", cal_score,)
    clusters=[]
    for i in range(_nClusters+1):
        clusters.append([])
    for i,j in zip(clusterer.labels_,data):
        if (i!=-1):
            clusters[i].append(j)
        """
        else:
            clusters[len(clusters)-1].append(j)"""
    return clusters

def procesado(data):
    data_final=data.groupby('Grupo')
    data_agrupada=[]
    data_pendiente=[]
    for index,grupo in data_final:
        if(len(grupo['Historico'])==16):
            data_agrupada.append(grupo['Historico'])
            #data_pendiente.append(grupo.Pendiente)
    #print len(data_agrupada)
    infoKMeans(data_agrupada,data_agrupada)
    clusters=KMeansClustering(data_agrupada,_nClusters)
    #clusters=HDBSCANclustering(data_agrupada)
    datos=getInfo(clusters)
    getPlot(clusters).show()
    print datos

def main():
    if (len(sys.argv)>1):
        archivo=sys.argv[1]
    else:
        archivo="../csv.txt"
    data=getRegistros0(parser(archivo))
    #data=rellenaUnSoloHueco(data)
    #calculaPendiente(data)
    procesado(data)

def calculaPendiente(data):
    anterior=data['Historico'].mean()
    pendiente=[]
    for his in data['Historico']:
        pendiente.append(his-anterior)
        anterior=his
    data['Pendiente']=pendiente
main()
