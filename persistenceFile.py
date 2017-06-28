#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import os
import numpy as np
from fpdf import FPDF
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import zipfile

nombreDatos= [  'Glucosa Media', 'Desviacion tipica','Glucosa maxima media',
                'Glucosa minima media','Porcentaje de tiempo en rango 70-180',
                'Numero medio de eventos por debajo del minimo(60)',
                'Numero medio de eventos por encima del maximo (240)',
                'Maximo numero de eventos fuera de rango(60-240)',
                'Minimo numero de eventos fuera de rango(60-240)']

def getPlotAndSave(clusters,ruta,metodo,nombreArchivo):
    n_clusters=len(clusters)
    for i in range(n_clusters):
        for group in clusters[i]:
            if (n_clusters<4):
                plt.subplot(1,3,i+1)
            elif (n_clusters<5):
                plt.subplot(2,2,i+1)
            elif (n_clusters<7):
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
            elif(n_clusters<=36):
                plt.subplot(6,6,i+1)
            plt.plot(group)
            plt.axis([0,15,40,350])
    plt.savefig(ruta+nombreArchivo+'_'+metodo+'_'+str(n_clusters)+'_img.png')

def genTablaOrigin(code,pdf):
    pdf.cell(10,8,'','LTBR',0,'C',0)
    pdf.cell(28,8,'00-04',1,0,'C',0)
    pdf.cell(28,8,'04-08',1,0,'C',0)
    pdf.cell(28,8,'08-12',1,0,'C',0)
    pdf.cell(28,8,'12-16',1,0,'C',0)
    pdf.cell(28,8,'16-20',1,0,'C',0)
    pdf.cell(28,8,'20-24',1,0,'C',0)
    pdf.ln()
    n=1
    for cluster in code:
        pdf.cell(10,8,str(n),1,0,'C',0)
        for tramo in cluster:
            pdf.cell(28,8,str(tramo),1,0,'C',0)
        n+=1
        pdf.ln()
    return pdf

def genParam(clusters,metodo):
    n=0
    tra=0
    for tramos in clusters:
        n+=1
        for tramo in tramos:
            tra+=1
    param=""
    param+="En este caso se ha optado por la tecnica de clustering conocida como "
    param+=metodo
    param+=", tras haber identificado hasta "
    param+=str(tra)
    param+=" tramos validos y completos, los hemos asociado en "
    param+=str(n)
    param+=" grupos, llamados clusters de ahora en adelante."
    if (metodo=='hdbscan'):
        param+=" Notese que el ultimo de los clusters correspodiente al ruido, es decir, no compone un cluster en si mismo."
    return param

def genDescGraf(codes):
    frase=""
    for cluster,nCluster in zip(codes,range(len(codes))):
        frase+="El cluster numero "+ str(nCluster+1)+" esta formado por "
        salto=False
        for tramo, nTramo in zip(cluster,range(len(cluster))):
            if(tramo>0):
                salto=True;
                if(tramo==1):
                    frase+= "1 tramo correspodiente "
                elif(tramo>1):
                    frase+= str(tramo)+" tramos correspondientes "
                frase+="a las horas entre "
                if(nTramo==0):
                    frase+="medianoche y las 4 am, "
                elif(nTramo==1):
                    frase+="las 4 am y las 8 am, "
                elif(nTramo==2):
                    frase+="las 8 am y mediodia, "
                elif(nTramo==3):
                    frase+="mediodia y las 4 pm, "
                elif(nTramo==4):
                    frase+="las 4 pm y las 8 pm, "
                elif(nTramo==5):
                    frase+="las 8 pm y medianoche."
        if (salto):
            frase+='\n'
    return frase

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
        nMaxDeEventosMalos=0
        sumaDeEventosMalosGrupo=0
        for group in clusters[i]:
            sumaDeMedias+=group.mean()
            sumaDeMaximos+=group.max()
            sumaDeMinimos+=group.min()
            nSegmentos+=1
            sumaDeEventosMalosGrupo=0
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

def genTabla(clusters,pdf):
    info=getInfo(clusters)
    pdf.cell(10,8,'','LTBR',0,'C',0)
    pdf.cell(20,8,'A',1,0,'C',0)
    pdf.cell(20,8,'B',1,0,'C',0)
    pdf.cell(20,8,'C',1,0,'C',0)
    pdf.cell(20,8,'D',1,0,'C',0)
    pdf.cell(20,8,'E',1,0,'C',0)
    pdf.cell(20,8,'F',1,0,'C',0)
    pdf.cell(20,8,'G',1,0,'C',0)
    pdf.cell(20,8,'H',1,0,'C',0)
    pdf.cell(20,8,'I',1,0,'C',0)
    pdf.ln()
    n=1
    for cluster in info:
        pdf.cell(10,8,str(n),1,0,'C',0)
        for dato,d in zip(cluster,range(len(cluster))):
            if (d<4 or d==5 or d==6):
                pdf.cell(20,8,str(round(dato,2)),1,0,'C',0)
            elif(d==4):
                pdf.cell(20,8,str(round(dato,2))+'%',1,0,'C',0)
            elif(d>=7):
                pdf.cell(20,8,str(int(dato)),1,0,'C',0)
        n+=1
        pdf.ln()
    return pdf

def saveData(ruta,etiquetas,nombres,datos,metodo,nombreArchivo=""):
    nCarpetas=max(etiquetas)
    os.mkdir(ruta+"clusters")
    for i in range(nCarpetas+1):
        os.mkdir(ruta+'clusters/'+str(i))
    for cluster,nombre,dato in zip(etiquetas,nombres,datos):
        np.savetxt(ruta+'clusters/'+str(cluster)+'/'+str(nombre),dato,fmt='%i',delimiter=" ")
    fantasy_zip = zipfile.ZipFile(ruta+nombreArchivo+'_'+metodo+'_'+str(nCarpetas+1)+'.zip ', 'w')
    for root, dirs, files in os.walk(ruta+'clusters/'):
        for file in files:
            fantasy_zip.write(os.path.join(root, file))
    fantasy_zip.close()

def genLatex(clusters,code,metodo):
    n=0
    tra=0
    for tramos in clusters:
        n+=1
        for tramo in tramos:
            tra+=1
    frase=""
    frase+='\section{Informe gluc\'{e}mico}\n Aplicando una serie de t\'{e}cnicas basadas en el aprendizaje autom\'{a}tico,'
    frase+='se realiza un estudio sobre los patrones que reflejan sus niveles de glucosa en tramos de cuatro horas, comenzando desde las 00:00h. Cada fragmento pertenece por tanto a una franja horario:\n'
	frase+="\\begin{itemize}\n \item Franja 0 : de medianoche (00:00h) a las 04:00h\n \item Franja 1 : de 04:00h a las 08:00h\n"
    frase+="\item Franja 2 : de 00.08h a medio\'{i}a (12:00h) \n \item Franja 3 : de  medio\'{i}a (12:00h) a las 16:00h \n \item Franja 4 : de 16:00h a las 20:00h \n\item Franja 5 : de las 20:00h  a medianoche (00:00h)\n \end{itemize}\n"
	frase+='En este caso se ha optado por la t\'{e}cnica de clustering conocida como \textit{'+ metodo
    frase+=", tras haber identificado hasta "+ str(tra)
    frase+=" tramos v\'{a}lidos y completos, los hemos asociado en " str(n)
    frase+=" grupos o clusters. \n"
    if (metodo=='hdbscan'):
        frase+=" N\'{o}tese que el \'{u}ltimo de los clusters correspodiente al ruido, es decir, no compone un cluster en si mismo."

    frase+='Cada una de las \'{i}neas que ver\'{a}en las gr\'{a}ficas representa un fragmento de 4 horas distinto. Cada uno de estos clusters puede caracterizarse seg\'{u}n unas m\'{e}tricas estad\'{i}sticas que se muestran en la tabla \ref{tab:param}.'
	frase+= 'De cada cluster (enumerados de 1 en adelante, de izquierda a derecha y de arriba a abajo) detallaremos a la cantidad de fragmentos de cada tramo horario que contiene y los caracterizaremos por un conjunto de m\'{e}tricas estad\'{i}sticas.\n'
	frase+='\subsection{Descripci\'{o}n de las agrupaciones}\n La tabla \ref{tab:clusterdescription} muestra la frecuencia de cada tramo horario en cada uno de los clusters. Esta tabla se puede resumir en: \begin{enumerate}\n'
    for cluster,nCluster in zip(code,range(len(code))):
        frase+="\item El cluster n\'{u}mero "+ str(nCluster+1)+" esta formado por "
        salto=False
        for tramo, nTramo in zip(cluster,range(len(cluster))):
            if(tramo>0):
                salto=True;
                if(tramo==1):
                    frase+= "1 tramo correspodiente "
                elif(tramo>1):
                    frase+= str(tramo)+" tramos correspondientes "
                frase+="a las horas entre "
                if(nTramo==0):
                    frase+="0h y las 4 am, "
                elif(nTramo==1):
                    frase+="las 4 am y las 8 am, "
                elif(nTramo==2):
                    frase+="las 8 am y 12am, "
                elif(nTramo==3):
                    frase+="12 y las 4 pm, "
                elif(nTramo==4):
                    frase+="las 4 pm y las 8 pm, "
                elif(nTramo==5):
                    frase+="las 8 pm y medianoche."
        if (salto):
            frase+='\n'
	frase+='\end{enumerate}\n \begin{table}[ht]\n \caption{Composici\'{o}n de los clusters obtenidos mediante \textit{'+ metodo +'}. N\'{u}mero de los tramos de cada franja horaria que contiene cada cluster}\n \centering\n \begin{tabular}{|c|c|c|c|c|c|c|}\n \hline\n Cluster & Franja 0 & Franja 1& Franja 2& Franja 3& Franja 4& Franja 5 \n \hline'
    for cluster in code:
        frase+=str(n)+'&'
        for tramo,nTramo in zip(cluster,range(len(cluster))):
            if (nTramo<len(cluster)-1):
				frase+=str(tramo)+'&'
			else:
				frase+=str(tramo)+'//\n'
        n+=1

	frase+='\hline \n\end{tabular}\n\label{tab:clusterdescription}\n\end{table}\n La caracterizaci\'{o}n de los clusters se presenta en la tabla \ref{tab:carac} atendiendo a las siguientes variables \n \begin{itemize}\n \item (A) - Glucosa Media\n \item (B) - Desviación típica\n\item (C) - Glucosa máxima media'
	frase+='\n\item (D) - Glucosa mínima media\n\item (E) - Porcentaje de tiempo en rango 70-180\n\item (F)- Número medio de eventos por debajo del mínimo(60)\n \item (G) - Número medio de eventos por encima del máximo (240)\n \item (H) - Máximo número de eventos fuera de rango(60-240)\n \item (I) - Mínimo número de eventos fuera de rango(60-240)\n\end{itemize}\n'
	frase+='\begin{table}[]\n \centering \n\caption{Caracterizaci\'{o}n de los clusters obtenidos mediante \textit{K-means}.}\n\label{tab:carac}\n\begin{tabular}{|llllllllll|}\n\hline \n &A & B      & C     & D      & E      & F       & G    & H    & I     \\\n\hline'
	for cluster in info:
        for dato,d in zip(cluster,range(len(cluster))):
            if (d<4 or d==5 or d==6):
                frase+=str(round(dato,2))+' & '
            elif(d==4):
                frase+=str(round(dato,2))+' \% & '
            elif(d==7):
                frase+=str(int(dato))+' & '
			elif(d==8):
                frase+=str(int(dato))+' \\ \n '

	frase+='\hline\n \end{tabular}\n\end{table}\n'
    return frase

def toLatex(clusters, code, metodo,ruta=""):
    file=open(ruta+"file.tex","w")
    file.write(genLatex(clusters,code,metodo))
    file.close()


def toPDF(clusters,codes,metodo,ruta="",nombreArchivo=""):
    nucleos=len(clusters)
    route="/home/tfg/main/meanSerpentForestSRC/"
    pdf=FPDF('P','mm','A4')
    pdf.add_page()
    titulo="Informe sobre glucemia"
    w = len(titulo) + 6
    pdf.set_x((210 - w) / 2)
    pdf.set_font('Times','B',20)
    pdf.cell(w,9,titulo,0,1,'C',0)
    pdf.ln()
    pdf.set_font('Times','',12)
    with open(route+'Introduccion', 'rb') as fh:
        intro = fh.read().decode('utf-8')
    pdf.multi_cell(0,5,intro)
    pdf.ln()
    param=genParam(clusters,metodo)
    pdf.multi_cell(0,5,param)
    with open(route+'explica', 'rb') as fh:
        pos = fh.read().decode('utf-8')
    pdf.multi_cell(0,5,pos)
    getPlotAndSave(clusters,ruta,metodo,nombreArchivo)
    pdf.image(ruta+nombreArchivo+'_'+metodo+'_'+str(nucleos)+'_img.png', 0,pdf.get_y() ,8*28)
    pdf.add_page()
    pdf.multi_cell(0,5,genDescGraf(codes))
    pdf.ln()
    pdf.ln()
    pdf.ln()
    pdf=genTablaOrigin(codes,pdf)
    pdf.add_page()
    with open(route+'lista', 'rb') as fh:
        intro = fh.read().decode('utf-8')
    pdf.multi_cell(0,5,intro)
    pdf.ln()
    pdf.ln()
    pdf=genTabla(clusters,pdf)
    pdf.add_page()
    with open(route+'responsabilidad', 'rb') as fh:
        res = fh.read().decode('utf-8')
    pdf.multi_cell(0,5,res,border=1)
    pdf.output(ruta+nombreArchivo+'_'+metodo+'_'+str(nucleos)+'_informe.pdf','F')
    return str(nombreArchivo+'_'+metodo+'_'+str(nucleos)+'_informe.pdf')
