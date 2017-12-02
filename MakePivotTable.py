import pandas as pd
from GroceryUtil import *
import config
import sqlite3

pivotTable = config.pivotTable
db = config.db
trainTable = config.trainTable
itemsTable = config.itemsTable
storesTable = config.storesTable
transactionsTable = config.transactionsTable
testTable = config.testTable


conn = sqlite3.connect(db)
cur = conn.cursor()

def appendPivot(trainQuery, conn):
    print "loading training data"
    trainDF = pd.read_sql_query(trainQuery, conn)

    train = cleanTrainSet(trainDF)
    dates = pd.date_range('2016-01-01', '2017-08-15')
    train = imputeTrainSet(train, dates)


    pivotTrain = train.pivot_table(index = ['store_nbr', 'item_nbr'], columns='date', values = 'unit_sales')

    pivotTrain.to_sql(pivotTable, conn, if_exists='append')


trainQuery = "SELECT date, store_nbr, item_nbr, unit_sales FROM " + trainTable + " " + """
                                WHERE store_nbr = 1
                                AND (date >= '2016-01-01') ;"""

dropTable(pivotTable, cur)

for i in range(1,55):
    trainQuery = ("SELECT date, store_nbr, item_nbr, unit_sales FROM " + trainTable + " "
                                + "WHERE store_nbr = " + str(i) + " "
                                + "AND (date >= '2016-01-01') ;")
    appendPivot(trainQuery, conn)
    print "done with store " + str(i)