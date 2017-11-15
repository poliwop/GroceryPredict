import pandas as pd
import sqlite3
db = "GroceryPredictNew.db"
dataPath = 'C:/Users/Colin/Documents/GroceriesPredict/Data/'

traincsvfile = 'train.csv'
itemscsvfile = 'items.csv'
storescsvfile = 'stores.csv'
transactionscsvfile = 'transactions.csv'
testcsvfile = 'test.csv'

trainTable = 'trainInput'
itemsTable = 'itemsInput'
storesTable = 'storesInput'
transactionsTable = 'transactionsInput'
testTable = 'testInput'

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

def exists(tableName, cur):
    statement = "SELECT name FROM sqlite_master WHERE type='table';"
    if (tableName,) in cur.execute(statement).fetchall():
        return True
    else:
        return False

def dropTable(tableName, cur):
    if exists(tableName, cur):
        print("Dropping " + tableName)
        cur.execute("DROP TABLE " + tableName)

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


# print "loading items csv"
# df = pd.read_csv(dataPath + itemscsvfile, dtype = dtypes)
# print "moving csv to db"
# importTable(df, itemsTable)
#
# print "loading stores csv"
# df = pd.read_csv(dataPath + storescsvfile, dtype=dtypes)
# print "moving csv to db"
# importTable(df, storesTable)
#
# print "loading transactions csv"
# df = pd.read_csv(dataPath + transactionscsvfile, dtype = dtypes, parse_dates=['date'])
# print "moving csv to db"
# importTable(df, transactionsTable)
#
# print "loading test csv"
# df = pd.read_csv(dataPath + testcsvfile, dtype = dtypes, parse_dates=['date'])
# print "moving csv to db"
# importTable(df, testTable)
