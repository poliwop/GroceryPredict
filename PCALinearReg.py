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

def getPCAFunction(pcaCoefs):
    return lambda x: np.matmul(pcaCoefs,np.transpose(x))

def getAllItems():
    q = "SELECT item_nbr FROM " + itemsTable + ";"
    itemsDF = pd.read_sql_query(q, conn)
    return itemsDF['item_nbr'].tolist()

#def getSalesListI(date, trainPivot):


def getPCAVars(transformMat, df, trainPivot):
    PCAVarList = [None]*len(df)
    for input in df.iterrows():
        date = input[1]["date"]
        store_nbr = input[1]["store_nbr"]
        item_nbr = input[1]["item_nbr"]
        lastDate = date - dt.timedelta(days = predictionLag)
        #firstDate = lastDate - dt.timedelta(days = windowLength)
        #test1 = trainPivot[firstDate]
        #test2 = trainPivot.columns.get_loc(firstDate)
        lastI = trainPivot.columns.get_loc(lastDate)
        row = trainPivot.loc[(store_nbr, item_nbr)]
        sales = row[(lastI - windowLength + 1):(lastI + 1)]
        salesList = sales.tolist()
        PCAVars = np.matmul(transformMat, np.transpose(salesList))
        PCAVarList[input[0]] = PCAVars
    return PCAVarList

    # for each row in df, retrieve indices to get data from trainPivot
    #   get data from indices
    #   apply transformMat to

    # return list of PCAVars


def getPCA(train, test):
    train = cleanTrainSet(train)
    train = imputeTrainSet(train, dateList = pd.date_range('2017-05-01', '2017-07-31'))
                                  #itemList = getAllItems())
    test['date'] = pd.to_datetime(test['date'])
    print "pivoting"
    trainPivot = train.pivot_table(index = ['store_nbr', 'item_nbr'], columns='date', values = 'unit_sales')

    # initialize data frame

    nWindows = len(trainPivot.columns) - windowLength + 1
    rowCount = nWindows * len(trainPivot)

    #df1 = pd.DataFrame(None, index=range(rowCount), columns=['date'], dtype = 'datetime64')
    dateList = [None]*rowCount
    #df2 = pd.DataFrame(0, index=range(rowCount), columns=['store_nbr'], dtype = 'int')
    storeList = [0]*rowCount
    #df3 = pd.DataFrame(0, index=range(rowCount), columns=['item_nbr'], dtype = 'int')
    itemList = [0]*rowCount
    #df4 = pd.DataFrame([0.0]*windowLength, index=range(rowCount), columns=['salesArray'])
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

    #input = {"date": dateList, "store_nbr": storeList, "item_nbr": itemList, "salesArray": salesList}
    input = {"date": dateList, "store_nbr": storeList, "item_nbr": itemList}
    print 'building DF'
    inputDF = pd.DataFrame(input)
    inputDF["date"] = pd.to_datetime(inputDF["date"])
    print 'building training DF'
    #df.loc[:, 'B'] > 0
    testI = (inputDF.loc[:, "date"] < testStartDate).tolist()
    slidingData = list(compress(salesList, testI))
    trainingDF = inputDF[inputDF["date"] < testStartDate]
    print 'getting sliding windows'
    #slidingData = trainingDF["salesArray"].tolist()

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
    #PCAFunction = getPCAFunction(transformMat)
    trainVars = getPCAVars(transformMat, train, trainPivot)
    #train["PCAvars"] = train["salesArray"].apply(PCAFunction)
    #nullInds = np.where(test['salesArray'].isnull())[0]
    #for i in nullInds:
    #test.loc[nullInds, "salesArray"] = [np.zeros_like(test.iloc[0,4])]*len(nullInds)
    #test["PCAvars"] = test["salesArray"].apply(PCAFunction)
    testVars = getPCAVars(transformMat, test, trainPivot)


    #trainVars = train["PCAvars"].tolist()
    #testVars = test["PCAvars"].tolist()
    trainTargets = train["unit_sales"]

    regr = linear_model.LinearRegression()
    regr.fit(np.asarray(trainVars), trainTargets)
    logresults = regr.predict(np.asarray(testVars))
    results = pd.DataFrame(np.expm1(logresults), columns = ["unit_sales"])
    results["id"] = test["id"]
    return results
