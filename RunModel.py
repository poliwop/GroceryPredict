import pandas as pd
import sqlite3
import math
from MovingAverages import *
from PCALinearReg import *
from scoreQuery import score
import config
import cProfile
from datetime import timedelta

db = config.db
trainTable = config.smallTrainTable
itemsTable = config.itemsTable
storesTable = config.storesTable
transactionsTable = config.transactionsTable
testTable = config.testTable

resultsTable = 'PCAResults'
trainQuery = "SELECT date, store_nbr, item_nbr, unit_sales FROM " + trainTable + " " + """  
                                WHERE date >= '2017-05-01'
                                AND date < '2017-08-01';"""
trainQuery2 = "SELECT date, store_nbr, item_nbr, unit_sales FROM " + trainTable + " LIMIT 5;"
#trainQuery = "SELECT date, store_nbr, item_nbr, unit_sales FROM " + trainTable + " LIMIT 5;"
# item 96995, 99197, 1388521

testQuery = "SELECT id, date, store_nbr, item_nbr, unit_sales FROM " + trainTable + " " + """
                                WHERE date >= '2017-08-01';"""
testQuery2 = "SELECT id, date, store_nbr, item_nbr, unit_sales FROM " + trainTable + " LIMIT 10;"
#testQuery = "SELECT id, date, store_nbr, item_nbr FROM " + trainTable + " LIMIT 5;"


conn = sqlite3.connect(db)
cur = conn.cursor()

print "loading training data"
trainDF = pd.read_sql_query(trainQuery, conn)

print "loading testing data"
testDF = pd.read_sql_query(testQuery, conn)

print "cleaning data"
trainDF = cleanTrainSet(trainDF)
train = imputeTrainSet(trainDF, dateList=pd.date_range('2017-05-01', '2017-07-31'),
                       itemList=getAllItems())
train = fillNans(train)
testDF = cleanTrainSet(testDF)
testDF = imputeTrainSet(testDF, dateList=pd.date_range('2017-08-01', '2017-08-15'),
                      itemList=getAllItems())
testDF = fillNans(testDF)

test = testDF.drop(['unit_sales'], axis=1, inplace=False)



#df = MovingAverages(trainDF, test)
df = getPCA(train, test)
#cProfile.run(getPCA(trainDF, test))

items = pd.read_sql_query("SELECT item_nbr, perishable FROM " + itemsTable + ";", conn)
testDF = pd.merge(testDF, items, how='left', on='item_nbr')
testDF.rename(columns = {'unit_sales':'actual_unit_sales'}, inplace = True)
testDF.drop(['id'], axis=1, inplace = True)
df = pd.merge(df, testDF, how='left', on=['date', 'store_nbr', 'item_nbr'])
df = df[['id', 'unit_sales', 'actual_unit_sales', 'perishable']]

print "Score: " + str(score(df))
# create output table
df.to_sql(resultsTable, con = conn, if_exists = 'replace', index = False)


cur.close()
