import pandas as pd
import numpy as np
import sys
import time
import timeit
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.cluster import KMeans
from sklearn.utils import check_random_state, shuffle

valorMinimo=8

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

def agrupar(data):
    contadorDeApariciones = data['Grupo'].value_counts(sort=False)
    grupo=0
    for a in contadorDeApariciones:#esto es muy ineficiente
        if (a!=16 or a<valorMinimo):
            data=data[data.Grupo!=grupo]
        elif(a>=valorMinimo and a<16):
            rowsNeeded=16-a
        grupo=grupo+1
    data_agrupada=data.groupby('Grupo')
    #print data.describe()
    return data_agrupada

def hazAlgoConEsto(clustering):#BSD http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_stability_low_dim_dense.html#sphx-glr-auto-examples-cluster-plot-kmeans-stability-low-dim-dense-py
    random_state = np.random.RandomState(0)

    # Number of run (with randomly generated dataset) for each strategy so as
    # to be able to compute an estimate of the standard deviation
    n_runs = 5

    # k-means models can do several random inits so as to be able to trade
    # CPU time for convergence robustness
    n_init_range = np.array([1, 5, 10, 15, 20])

    # Datasets generation parameters
    n_samples_per_center = 100
    grid_size = 3
    scale = 0.1
    n_clusters = grid_size ** 2


    def make_data(random_state, n_samples_per_center, grid_size, scale):
        random_state = check_random_state(random_state)
        centers = np.array([[i, j]
                            for i in range(grid_size)
                            for j in range(grid_size)])
        n_clusters_true, n_features = centers.shape

        noise = random_state.normal(
            scale=scale, size=(n_samples_per_center, centers.shape[1]))

        X = np.concatenate([c + noise for c in centers])
        y = np.concatenate([[i] * n_samples_per_center
                            for i in range(n_clusters_true)])
        return shuffle(X, y, random_state=random_state)
    X, y = make_data(random_state, n_samples_per_center, grid_size, scale)
    fig = plt.figure()
    for k in range(8):
        my_members = clustering.labels_ == k
        color = cm.spectral(float(k) / 8, 1)
        plt.plot(X[my_members, 0], X[my_members, 1], 'o', marker='.', c=color)
        cluster_center = clustering.cluster_centers_[k]
        plt.plot(cluster_center[0], cluster_center[1], 'o',
                 markerfacecolor=color, markeredgecolor='k', markersize=6)
        plt.title("Example cluster allocation with a single random init\n"
                  "with MiniBatchKMeans")
    plt.show()

def clustering(clustering):
    a=[]

def main():
    start = timeit.timeit()
    end = timeit.timeit()
    print "tiempo inicial"
    print end - start
    if (len(sys.argv)>1):
        archivo=sys.argv[1]
    else:
        archivo="../csv.txt"
    data=parser(archivo)
    data=filtro(data,0)
    print "entre filtro y agrupar"
    print timeit.timeit() - start
    data=agrupar(data)
    print "entre agrupar y convertir para KMeans"
    print timeit.timeit() - start
    data_agrupada=[]
    for index,grupo in data:
        data_agrupada.append(grupo['Historico'])
    print "convertidp para KMeans"
    print timeit.timeit() - start
    clustering=KMeans()
    clustering.fit(data_agrupada)
    #hazAlgoConEsto(clustering)
    print "Todo ha salido a pedir de boca"

main()
