import pandas as pd
import sqlite3
import datetime as dt
import config
import numpy as np
from sklearn.decomposition import PCA
from GroceryUtil import *
from sklearn import linear_model
import math

db = config.db
conn = sqlite3.connect(db)
cur = conn.cursor()

trainTable = config.trainTable
itemsTable = config.itemsTable
storesTable = config.storesTable
transactionsTable = config.transactionsTable
testTable = config.testTable
pivotTable = config.pivotTable

windowLength = 42
predictionLag = 16
startDate = dt.date(2017, 5, 1)
testStartDate = dt.date(2017, 8, 1)
nComponents = 10

def getPCAFunction(pcaCoefs):
    return lambda x: np.matmul(pcaCoefs,np.transpose(x))


def getPCA(train, test):
    train = cleanTrainSet(train)
    train = imputeTrainSet(train, pd.date_range('2017-05-01', '2017-07-31'))
    test['date'] = pd.to_datetime(test['date'])
    print "pivoting"
    trainPivot = train.pivot_table(index = ['store_nbr', 'item_nbr'], columns='date', values = 'unit_sales')

    inputDF = pd.DataFrame()
    dates = pd.DataFrame([startDate + dt.timedelta(windowLength + predictionLag + i) for i in range(len(trainPivot.columns) - windowLength + 1)], columns = ["date"])
    dates['date'] = pd.to_datetime(dates['date'])

    print "generating tuples"
    totalPoints = len(trainPivot)
    percPoints = math.ceil(totalPoints / float(100))
    print "total rows: " + str(len(trainPivot))
    ct = 0
    for salesRecord in trainPivot.itertuples():
        sales = np.asarray(salesRecord[1:])
        itemPoints = [sales[i:i + windowLength] for i in range(len(sales) - windowLength + 1)]
        slidingDF = pd.DataFrame()
        slidingDF["salesArray"] = itemPoints
        slidingDF["store_nbr"] = salesRecord[0][0]
        slidingDF["item_nbr"] = salesRecord[0][1]
        slidingDF["date"] = dates
        inputDF = inputDF.append(slidingDF)
        ct += 1
        if ct % 100 == 0:
            print str(ct/float(totalPoints)) + " done."

    trainingDF = inputDF[inputDF["date"] < testStartDate]
    slidingData = trainingDF["salesArray"].tolist()

    pca = PCA(n_components=nComponents)
    print "PCAing"
    pca.fit(slidingData)
    print(pca.explained_variance_ratio_)
    print(pca.components_)
    variation = pca.explained_variance_ratio_.cumsum()
    transformMat = pca.components_[0:nComponents]


    #Transform training data

    train = train[train['date'] >= '2017-07-01']
    train = pd.merge(train, trainingDF,  how = 'left', on=["date", "store_nbr", "item_nbr"])
    test = pd.merge(test, inputDF, how='left', on=["date", "store_nbr", "item_nbr"])
    train["PCAvars"] = train["salesArray"].apply(getPCAFunction(transformMat))
    test["PCAvars"] = test["salesArray"].apply(getPCAFunction(transformMat))

    trainVars = train["PCAvars"].tolist()
    testVars = test["PCAvars"].tolist()
    trainTargets = train["unit_sales"]

    regr = linear_model.LinearRegression()
    regr.fit(np.asarray(trainVars), trainTargets)
    logresults = regr.predict(np.asarray(testVars))
    results = pd.DataFrame(np.expm1(logresults), columns = ["unit_sales"])
    results["id"] = test["id"]
    return results
