import pandas as pd
import sqlite3
import math
import config
itemsTable = config.itemsTable

def scoreQuery(query, db):
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(query, conn)
    return score(df), len(df)

def score(df):
    predict = df['unit_sales'].apply(pd.np.log1p)
    df.loc[(df.actual_unit_sales < 0), 'actual_unit_sales'] = 0
    actual = df['actual_unit_sales'].apply(pd.np.log1p)
    temp = (predict - actual) ** 2
    weights = df['perishable'] / 4.0 + 1
    return math.sqrt(temp.dot(weights) / weights.sum())


db = config.db
#resultsTable = 'test'
resultsTable = 'results_view'
#whereQuery = "WHERE item_nbr IN (SELECT item_nbr FROM " + itemsTable + " WHERE family = 'BEVERAGES')"
whereQuery = "WHERE date = '2017-08-13 00:00:00'"

testQuery = "SELECT unit_sales, actual_unit_sales, perishable FROM " + resultsTable + " " + whereQuery + ";"

print scoreQuery(testQuery, db)

#ctQuery = "SELECT count(*) FROM " + resultsTable + " " + whereQuery + ";"
#conn = sqlite3.connect(db)
#df = pd.read_sql_query(ctQuery, conn)
#print df
