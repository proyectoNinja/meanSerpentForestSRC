import pandas as pd
import numpy as np
import sys
import os
import time
import timeit
import math
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, SpectralClustering, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.metrics.cluster import calinski_harabaz_score
from sklearn.preprocessing import Normalizer as norm
import hdbscan
import forest_cluster as rfc

nombreDatos= [  'Glucosa Media', 'Desviacion tipica','Glucosa maxima media',
                'Glucosa minima media','Porcentaje de tiempo en rango 70-180',
                'Numero medio de eventos por debajo del minimo(60)',
                'Numero medio de eventos por encima del maximo (240)',
                'Maximo numero de eventos fuera de rango(60-240)',
                'Minimo numero de eventos fuera de rango(60-240)']

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
    if(hora_<4 ):
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
    #data['Hora'].map(lambda x: get_group(x,primeraHora,format))
    data['Grupo']=data['Hora'].map(lambda x: gt_group(x,primeraHora,desplazamiento))
    #data['Grupo']=data['Hora'].map(lambda x: clasificaPorHora(x,primeraHora,format,desplazamiento))
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
    for fila,valor,grupo in zip(data.rows,data['Historico'],data['Grupo']):
        contadorGrupo+=1
        if (contadorGrupo==17):
            grupoActual+=1
            contadorGrupo=1
        if(hora+17-horaGuardada>0 and hora+17-horaGuardada<10):
            print "introducimos nuevo valor en ", hora+15
            data.loc
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

def getPlotAndSave(clusters):
    n_clusters=len(clusters)
    a=0
    for i in range(n_clusters):
        for group in clusters[i]:
            if (n_clusters<7):
                plt.subplot(2,3,i+1)
            elif(n_clusters<9):
                plt.subplot(2,4,i+1)
            elif(n_clusters==9):
                plt.subplot(3,3,i+1)
            elif(n_clusters==10):
                plt.subplot(2,5,i+1)
            elif(n_clusters<=16):
                plt.subplot(4,4,i+1)
            elif(n_clusters<=25):
                plt.subplot(5,5,i+1)
            plt.plot(group)
            plt.axis([0,15,40,350])
    #plt.savefig(os.path.join(sys.argv[1]+'invalido_graficas_'+sys.argv[2]+'.png'))
    plt.show()
    return plt

def randomForestClustering(datas,normalizar):
    if (normalizar):
        data=norm().fit_transform(datas)
    else:
        data=datas
    print rfc
    cluster_labels=rfc.RandomForestEmbedding().transform(data)
    print cluster_labels
    return cluster_labels

def KMeansNClustering(datas,n_clusters):
    data=norm().fit_transform(datas)
    clustering=KMeans(n_clusters=n_clusters, random_state=10)
    clustering.fit(data)
    clusters=[]
    for i in range(nclusters):
        clusters.append([])
    for i,j in zip(clustering.labels_,datas):
        clusters[i].append(j)
    return clusters

def KMeansClustering(datas,normalizar):
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
    clusters=[]
    for i in range(numero):
        clusters.append([])
    for i,j in zip(etiquetas,datas):
        clusters[i].append(j)
    return clusters

def clusteringAglomerativo(datas,normalizar):
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
            print("For n_clusters =", n_clusters+5,
                  "The average silhouette_score is : ", valor)
            if (valor>mejor):
                mejor=valor
                etiquetas=cluster_labels
                numero=n_clusters+5
        clusters=[]
        for i in range(numero):
            clusters.append([])
        for i,j in zip(etiquetas,datas):
            clusters[i].append(j)
        return clusters

def HDBSCANclustering(data):
    clusterer = hdbscan.HDBSCAN(metric='euclidean',min_cluster_size=2, min_samples=2)
    clusterer.fit(data)
    _nClusters=clusterer.labels_.max()+1
    silhouette_avg = silhouette_score(data, clusterer.labels_)
    cal_score = calinski_harabaz_score(data,clusterer.labels_)
    print("For n_clusters =", _nClusters-1,
          "The average silhouette_score is :", silhouette_avg,
          ", the calinski_harabaz score is ", cal_score)
    clusters=[]
    for i in range(_nClusters+1):
        clusters.append([])
    for i,j in zip(clusterer.labels_,data):
        if (i!=-1):
            clusters[i].append(j)
        else:
            clusters[_nClusters-1].append(j)
    return clusters

def procesado(data,metodo,nucleos=0):
    data_final=data.groupby('Grupo')
    data_agrupada=[]
    data_pendiente=[]
    clusters=[]
    for index,grupo in data_final:
        if(len(grupo['Historico'])==16):
            data_agrupada.append(grupo['Historico'])
    if (metodo=="kmeans"):
        clusters=KMeansClustering(data_agrupada,True)
    elif(metodo=="aglomerative"):
        clusters=clusteringAglomerativo(data_agrupada,True)
    elif(metodo=="hbdscan"):
        clusters=HDBSCANclustering(data_agrupada)
    elif(metodo=="nkmeans"):
        clusters=KMeansNClustering(data_agrupada,nucleos)
    plot = getPlotAndSave(clusters)
    plot.close()
    return zip(data_agrupada,clusters)

def main2():
    for param, index in zip(sys.argv,range(len(sys.argv))):
        if (index==1):
            data=getRegistros0(parser(param,index-1))
        elif(index>1):
            lectura=getRegistros0(parser(param,index-1))
            data=data.append(lectura)
    inOut=procesado(data,"nkmeans",nucleos=16)

def main():
    if (len(sys.argv)==1 or sys.argv[1]=="help"):
        print "AYUDA"
        print "El formato de entrada correspondiente para un solo csv es el siguiente"
        print "src.py [ruta y nombre del archivo][kmeans|aglomerative|hbdscan]"
        print "Opcionalmente un argumento numerico en [2,36] puede ir tras KMeans o aglomerative"
        exit()
    else:
        cluster="kmeans"
        nCluster=0
        archivo=sys.argv[1]
        if (len(sys.argv)>2):
            param=sys.argv[2]
            if(param=="kmeans"):
                cluster=param
                if(len(sys.argv)>3):
                    try:
                        nCluster=int(sys.argv[3])
                        cluster ="nkmeans"
                        if (nCluster>36 or nCluster<2):
                            raise
                    except Exception:
                        print "Esperamos un valor numerico en [2,20] para fijar el numero de clusters"
                        exit()
            elif(param=="aglomerative"):
                cluster=param
            elif(param=="hdbscan"):
                cluster=param
        data=getRegistros0(parser(archivo))
        procesado(data,cluster)

main()
