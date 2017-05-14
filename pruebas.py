import sys
import time
import timeit
import math
from datetime import datetime,timedelta

def get_codigoTramo(hora):
    tramo=0
    if (hora<4):
        tramo=0
    elif(hora<8):
        tramo=1
    elif(hora<12):
        tramo=2
    elif(hora<16):
        tramo=3
    elif(hora<20):
        tramo=4
    else:
        tramo=5
    return tramo

def get_group(hora,hMin):
    format="%Y/%m/%d %H:%M"
    group = 0
    hora_Actual=datetime.strptime(hora,format)
    hora_minima=datetime.strptime(hMin,format)
    dia0=hora_minima.day
    mes0=hora_minima.month
    anyo0=hora_minima.year
    hora_base=datetime.strptime(anyo0+"/"+mes0+"/"+dia0,"%Y/%m/%d")
    
