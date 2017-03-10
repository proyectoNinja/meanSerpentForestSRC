import pandas as pd
import time
import datetime

print "Leyendo archivo..."
data=pd.read_table('../csv.txt',header = 1, usecols=[1,2,3,4])
print data

print "Hecho"
