import pandas as pd
import numpy as np
import time
from datetime import datetime,timedelta

from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import KFold
from sklearn import cross_validation

def clasificaPorHora(hora,hMin):
    format="%Y/%m/%d %H:%M"
    hClasificar=datetime.strptime(hora,format)
    hRef=datetime.strptime(hMin,format)
    grupo=0
    clasificado=False
    while(grupo<89 and not clasificado):
        horas=4*(grupo+1)
        if(hRef+timedelta(hours=horas)>hClasificar):
            clasificado=True
        else:
            grupo=grupo+1
    return grupo

print "Leyendo archivo..."
columnas=['Hora','Tipo','Historico','Leida']
data=pd.read_table('../csv.txt',header = 1, usecols=[1,2,3,4],names=columnas,parse_dates=True)
data['Grupo']=data['Hora'].map(lambda x: clasificaPorHora(x,"2016/03/30 16:30"))
data.groupby(by="Grupo").mean
#output
columnas=['Hora','Tipo']
output=pd.read_csv('../out.csv',header = 0, usecols=[0,1],names=columnas,parse_dates=True)
output['Grupo']=output['Hora'].map(lambda x: clasificaPorHora(x,"2016/03/30 16:30"))
output.groupby(by="Grupo").mean
#predicciones
train_data= data.values
test_data= output.values
predictors=["Hora","Tipo","Grupo"]
target=["Historico","Leida"]
# Initialize our algorithm class
alg = RandomForestClassifier(random_state=1, n_estimators=390, min_samples_split=16, min_samples_leaf=4)
# We set random_state to ensure we get the same splits every time we run this.
kf = KFold(data.shape[0], n_folds=3, random_state=1)
"""
predictions = []
for train, test in kf:
    # The predictors we're using the train the algorithm.  Note how we only take the rows in the train folds.
    train_predictors = (data[predictors].iloc[train,:])
    # The target we're using to train the algorithm.
    train_target = (data[target].iloc[train,:])
    # Training the algorithm using the predictors and target.
    alg.fit(train_predictors, train_target)
    # We can now make predictions on the test fold
    test_predictions = alg.predict(data[predictors].iloc[test,:])
    predictions.append(test_predictions)

predictions = np.concatenate(predictions, axis=0)

print('imprimimos salida')
# submission--toCSV
submission = pandas.DataFrame({
        "Hora": output["Hora"],
        "Tipo": output["Tipo"],
        "Historico": predictions,
        "Leida": predictions
    })

submission.to_csv("../put_out.csv", index = False)
"""
print "Hecho"
