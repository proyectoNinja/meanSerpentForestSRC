#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime,timedelta
from sklearn.cluster import KMeans, SpectralClustering, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.metrics.cluster import calinski_harabaz_score
from sklearn.preprocessing import Normalizer as norm
import hdbscan
import persistenceFile

def getRegistros0(data):
    col=['Historico','Hora','Grupo']
    data=data[col]
    data=data.dropna(axis=0)
    format="%Y/%m/%d %H:%M"
    data.set_index('Hora', inplace=True)
    return data

def gt_group(hora,hMin,desplazamiento):
    format="%Y/%m/%d %H:%M"
    group = 0
    hora_Actual=datetime.strptime(hora,format)
    hora_minima=datetime.strptime(hMin,format)
    dia0=hora_minima.day
    mes0=hora_minima.month
    anyo0=hora_minima.year
    codigo=-1
    hora_=hora_Actual.hour
    min_=hora_Actual.minute
    if(hora_<4):
        codigo=0
    elif(hora_<8):
        codigo=1
    elif(hora_<12):
        codigo=2
    elif(hora_<16):
        codigo=3
    elif(hora_<20):
        codigo=4
    else:
        codigo=5
    string=str(anyo0)+"/"+str(mes0)+"/"+str(dia0)
    hora_base=datetime.strptime(string,"%Y/%m/%d")
    diferencia=hora_Actual-hora_base
    out=desplazamiento*1000+10*(diferencia.days)+codigo
    return out

def parser(dir,desplazamiento=0):
    columnas=['Hora','Tipo','Historico','Leida','Insulina rapida SV',
            'Insulina rapida U','Alimentos SV','Carbohidratos','Insulina lenta SV']
    data=pd.read_table(dir,header=1,usecols=[1,2,3,4,5,6,7,8,9],names=columnas)
    format="%Y/%m/%d %H:%M"
    primeraHora = data['Hora'].min()
    data['Grupo']=data['Hora'].map(lambda x: gt_group(x,primeraHora,desplazamiento))
    return data

def getStructCode(labels,nombre):
    nClusters=max(labels)+1
    code=[]
    for j in range(nClusters):
        code.append([])
        for i in range(6):
            code[j].append(0)
    for grupo,name in zip(labels,nombre):
        code[grupo][name%10]+=1
    return code

def getStructCluster(labels, data):
    clusters=[]
    numero=max(labels)+1
    for i in range(numero):
        clusters.append([])
    for i,j in zip(labels,data):
        clusters[i].append(j)
    return clusters

def KMeansNClustering(datas,nombre,n_clusters):
    data=norm().fit_transform(datas)
    clusterer=KMeans(n_clusters=n_clusters, random_state=10)
    return clusterer.fit_predict(data)

def KMeansClustering(datas,normalizar=True):
    etiquetas=[]
    mejor=0
    numero=0
    if (normalizar):
        data=norm().fit_transform(datas)
    else:
        data=datas
    for n_clusters in range(6):
        n=n_clusters+5
        clusterer = KMeans(n_clusters=n, random_state=10)
        cluster_labels = clusterer.fit_predict(data)
        valor = silhouette_score(data, cluster_labels)
        if (valor>mejor):
            mejor=valor
            etiquetas=cluster_labels
            numero=n
    return etiquetas

def clusteringAglomerativo(datas,normalizar=True):
        etiquetas=[]
        mejor=0
        numero=0
        if (normalizar):
            data=norm().fit_transform(datas)
        else:
            data=datas
        for n_clusters in range(6):
            clusterer = AgglomerativeClustering(n_clusters=n_clusters+5, affinity='manhattan',linkage='complete')
            cluster_labels = clusterer.fit_predict(data)
            valor = calinski_harabaz_score(data, cluster_labels)
            if (valor>mejor):
                mejor=valor
                etiquetas=cluster_labels
                numero=n_clusters+5
        return etiquetas

def clusteringNAglomerativo(data,nCluster):
    return AgglomerativeClustering(n_clusters=nCluster,affinity='manhattan',linkage='complete').fit_predict(norm().fit_transform(data))

def procesado(data,modo,metodo,ruta="./",nucleos=0,nombreArchivo=""):
    data_final=data.groupby('Grupo')
    data_agrupada=[]
    data_nombre=[]
    etiquetas=[]
    for index,grupo in data_final:
        if(len(grupo['Historico'])==16):
            data_agrupada.append(grupo['Historico'])
            data_nombre.append(index)
    data_norm=norm().fit_transform(data_agrupada)
    if (nucleos>0):
        if (metodo=="kmeans"):
            etiquetas=KMeans(n_clusters=nucleos, random_state=10).fit_predict(data_norm)
        elif(metodo=="aglomerative"):
            etiquetas=clusteringNAglomerativo(data_agrupada,nucleos)
    else:
        if (metodo=="kmeans"):
            etiquetas=KMeansClustering(data_agrupada)
            nucleos=etiquetas.max()+1
        elif(metodo=="aglomerative"):
            etiquetas=clusteringAglomerativo(data_agrupada)
            nucleos=etiquetas.max()+1
        elif(metodo=="hdbscan"):
            etiquetas=HDBSCANclustering(data_agrupada)
            nucleos=etiquetas.max()+1
            eti=[]
            for et in etiquetas:
                if (et==-1):
                    eti.append(nucleos)
                else:
                    eti.append(et)
            nucleos+=1
            etiquetas=eti
        else:
            exit()
    code=getStructCode(etiquetas,data_nombre)
    clusters=getStructCluster(etiquetas,data_agrupada)
    persistenceFile.saveData(ruta,etiquetas,data_nombre,data_agrupada,metodo,nombreArchivo)
    return persistenceFile.toPDF(clusters,code,metodo,ruta,nombreArchivo)

def mainWeb(rutas,metodo="kmeans",nucleos=0,nombreArchivo=""):
    data=getRegistros0(parser(rutas+"csv.txt"))
    procesado(data,"web",metodo,ruta=rutas,nucleos=nucleos,nombreArchivo=nombreArchivo)

def main():
    if (len(sys.argv)==1 or sys.argv[1]=="help"):
        print "AYUDA"
        print "El formato de entrada correspondiente para un solo csv es el siguiente"
        print "src.py [ruta_de_archivo][kmeans|aglomerative|hdbscan][num_clusters]"
        print "el archivo ha de llamarse csv.txt"
        print "num_clusters [2,36] solo puede ir tras KMeans o aglomerative"
        exit()
    else:
        cluster="kmeans"
        nCluster=0
        ruta=sys.argv[1]
        if(len(sys.argv)>2):
            param=sys.argv[2]
            if((param=="kmeans") or (param=="aglomerative")):
                cluster=param
                if(len(sys.argv)>3):
                    try:
                        nCluster=int(sys.argv[3])
                        if (nCluster>36 or nCluster<2):
                            raise
                    except Exception:
                        print "Esperamos un valor numerico en [2,20] para fijar el numero de clusters"
                        exit()
            elif(param=="hdbscan"):
                cluster=param
    data=getRegistros0(parser(ruta+"csv.txt"))
    print procesado(data,modo="terminal",metodo=cluster,ruta=ruta,nucleos=nCluster)


def HDBSCANclustering(data):
    clusterer = hdbscan.HDBSCAN(metric='l2',min_cluster_size=2, min_samples=1)
    clusterer.fit(data)
    return clusterer.labels_

if __name__ == "__main__":
    main()
#mainWeb(sys.argv[1])
