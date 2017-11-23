import pandas as pd
import sqlite3
import config
from GroceryUtil import *
db = config.db
dataPath = config.dataPath

traincsvfile = config.traincsvfile
itemscsvfile = config.itemscsvfile
storescsvfile = config.storescsvfile
transactionscsvfile = config.transactionscsvfile
testcsvfile = config.testcsvfile

trainTable = config.trainTable
itemsTable = config.itemsTable
storesTable = config.storesTable
transactionsTable = config.transactionsTable
testTable = config.testTable

dtypes = {'id':'int64', 'item_nbr':'int32', 'store_nbr':'int8', 'perishable':'int8', 'class':'int32', 'cluster':'int8',
          'transactions':'int32'}

print "connecting to DB"
conn = sqlite3.connect(db)
cur = conn.cursor()

def dispTop(tableName, cur):
    cur.execute("SELECT * FROM " + tableName + " LIMIT 5")
    rows = cur.fetchall()

    for row in rows:
        print(row)

def importTable(df, tableName):
    dropTable(tableName, cur)
    df.to_sql(tableName, conn, if_exists='append', index=False)
    dispTop(tableName, cur)



print "loading training csv"
#df = pd.read_csv(dataPath + traincsvfile, usecols=[1, 2, 3, 4], dtype=dtypes, parse_dates=['date'],
 #                    skiprows=range(1, 101688779))
df = pd.read_csv(dataPath + traincsvfile, dtype=dtypes, parse_dates=['date'])
print "moving csv to db"
importTable(df, trainTable)


print "loading items csv"
df = pd.read_csv(dataPath + itemscsvfile, dtype = dtypes)
print "moving csv to db"
importTable(df, itemsTable)

print "loading stores csv"
df = pd.read_csv(dataPath + storescsvfile, dtype=dtypes)
print "moving csv to db"
importTable(df, storesTable)

print "loading transactions csv"
df = pd.read_csv(dataPath + transactionscsvfile, dtype = dtypes, parse_dates=['date'])
print "moving csv to db"
importTable(df, transactionsTable)

print "loading test csv"
df = pd.read_csv(dataPath + testcsvfile, dtype = dtypes, parse_dates=['date'])
print "moving csv to db"
importTable(df, testTable)
