import pandas as pd
import sqlite3
import datetime as dt
import config
import numpy as np
from sklearn.decomposition import PCA
from GroceryUtil import *
from sklearn import linear_model
from itertools import compress
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

def getLastDateFunction(lag):
    return lambda x: x - dt.timedelta(days = lag)

def getAllItems():
    q = "SELECT item_nbr FROM " + itemsTable + ";"
    itemsDF = pd.read_sql_query(q, conn)
    return itemsDF['item_nbr'].tolist()

def getRowI(row, trainPivot):
    return trainPivot.loc(row['store_nbr'], row['item_nbr'])

#def getSales(row, lastI)
#    return row[]


def getPCAVars(transformMat, df, trainPivot):
    PCAVarList = [None]*len(df)
    numRows = len(df)
    lastDateSeries = df["date"].apply(lambda x: x - dt.timedelta(days = predictionLag))
    #rows = df.apply(getRowI, args = trainPivot, axis=1)
    lastI = lastDateSeries.apply(lambda x: trainPivot.columns.get_loc(x))
    #rows["lastI"] = lastI


    for input in df.iterrows():
        #lastDate = input[1]["date"] - dt.timedelta(days = predictionLag)
        #lastI = trainPivot.columns.get_loc(lastDate)
        row = trainPivot.loc[(input[1]["store_nbr"], input[1]["item_nbr"])]
        i = input[0]
        sales = row[(lastI[i] - windowLength + 1):(lastI[i] + 1)]
        salesList = sales.tolist()
        PCAVars = np.matmul(transformMat, np.transpose(salesList))
        PCAVarList[i] = PCAVars

        if input[0] % 10000 == 0:
            print str(input[0]) + " out of " + str(numRows) + " done"

    return PCAVarList


def getPCA(train, test):
    #train = cleanTrainSet(train)
    #train = imputeTrainSet(train, dateList = pd.date_range('2017-05-01', '2017-07-31'),
    #                              itemList = getAllItems())
    #train = fillNans(train)
    #test = imputeTrainSet(test, dateList=pd.date_range('2017-08-01', '2017-08-15'),
    #                            itemList=getAllItems())
    #test['date'] = pd.to_datetime(test['date'])
    #test.reset_index(inplace=True)
    print "pivoting"
    trainPivot = train.pivot_table(index = ['store_nbr', 'item_nbr'], columns='date', values = 'unit_sales')

    # initialize data frame

    nWindows = len(trainPivot.columns) - windowLength + 1
    rowCount = nWindows * len(trainPivot)

    dateList = [None]*rowCount
    storeList = [0]*rowCount
    itemList = [0]*rowCount
    salesList = [[0.0]*windowLength]*rowCount
    dates = [startDate + dt.timedelta(windowLength + predictionLag + i) for i in range(nWindows)]
    dateList = sum([dates]*len(trainPivot), [])


    print "generating tuples"
    print "total rows: " + str(len(trainPivot))
    ct = 0
    I = [nWindows*i for i in range(len(trainPivot))]
    for salesRecord in trainPivot.itertuples():
        sales = np.asarray(salesRecord[1:])
        itemPoints = [sales[i:i + windowLength] for i in range(nWindows)]

        storeList[I[ct]:(I[ct] + nWindows)] = [salesRecord[0][0]]*nWindows
        itemList[I[ct]:(I[ct] + nWindows)] = [salesRecord[0][1]]*nWindows
        salesList[I[ct]:(I[ct] + nWindows)] = itemPoints
        ct += 1
        if ct % 1000 == 0:
            print str(ct/float(rowCount)) + " done."

    input = {"date": dateList, "store_nbr": storeList, "item_nbr": itemList}
    print 'building DF'
    inputDF = pd.DataFrame(input)
    inputDF["date"] = pd.to_datetime(inputDF["date"])
    print 'building training DF'
    testI = (inputDF.loc[:, "date"] < testStartDate).tolist()
    slidingData = list(compress(salesList, testI))
    trainingDF = inputDF[inputDF["date"] < testStartDate]
    print 'getting sliding windows'

    pca = PCA(n_components=nComponents)
    print "PCAing"
    pca.fit(slidingData)
    variation = pca.explained_variance_ratio_.cumsum()
    transformMat = pca.components_[0:nComponents]

    #Transform training data

    train = train[train['date'] >= '2017-07-01']
    train = pd.merge(train, trainingDF,  how = 'left', on=["date", "store_nbr", "item_nbr"])
    test = pd.merge(test, inputDF, how='left', on=["date", "store_nbr", "item_nbr"])

    trainVars = getPCAVars(transformMat, train, trainPivot)
    testVars = getPCAVars(transformMat, test, trainPivot)

    trainTargets = train["unit_sales"]

    regr = linear_model.LinearRegression()
    regr.fit(np.asarray(trainVars), trainTargets)
    logresults = regr.predict(np.asarray(testVars))
    test["unit_sales"] = np.expm1(logresults)
    return test
