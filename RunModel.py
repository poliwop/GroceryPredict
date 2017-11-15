import pandas as pd
import sqlite3
import math
from MovingAverages import *
import scoreQuery
from datetime import timedelta

db = "GroceryPredict.db"
resultsTable = 'test'
trainQuery = """SELECT date, store_nbr, item_nbr, unit_sales FROM trainInput
                                WHERE date >= '2017-01-01'
                                AND date < '2017-08-01';"""
trainQuery2 = "SELECT date, store_nbr, item_nbr, unit_sales FROM trainInput LIMIT 5;"
#trainQuery = "SELECT date, store_nbr, item_nbr, unit_sales FROM trainInput LIMIT 5;"


testQuery = "SELECT id, date, store_nbr, item_nbr, unit_sales FROM trainInput WHERE date >= '2017-08-01';"
testQuery2 = "SELECT id, date, store_nbr, item_nbr, unit_sales FROM trainInput LIMIT 10;"
#testQuery = "SELECT id, date, store_nbr, item_nbr FROM trainInput LIMIT 5;"


conn = sqlite3.connect(db)
cur = conn.cursor()

print "loading training data"
trainDF = pd.read_sql_query(trainQuery, conn)

print "loading testing data"
testDF = pd.read_sql_query(testQuery, conn)
test = testDF.drop(['unit_sales'], axis=1, inplace=False)


df = MovingAverages(trainDF, test)


items = pd.read_sql_query("SELECT item_nbr, perishable FROM itemsInput;", conn)
testDF = pd.merge(testDF, items, how='left', on='item_nbr')
testDF.rename(columns = {'unit_sales':'actual_unit_sales'}, inplace = True)
df = pd.merge(df, testDF, how='left', on='id')
df = df[['id', 'unit_sales', 'actual_unit_sales', 'perishable']]

print "Score: " + str(scoreQuery.score(df))
# create output table
df.to_sql(resultsTable, con = conn, if_exists = 'replace', index = False)


cur.close()
