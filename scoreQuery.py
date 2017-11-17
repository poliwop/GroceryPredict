import pandas as pd
import sqlite3
import math
import config

def scoreQuery(query, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    df = pd.read_sql_query(query, conn)
    return score(df)

def score(df):
    predict = df['unit_sales'].apply(pd.np.log1p)
    df.loc[(df.actual_unit_sales < 0), 'actual_unit_sales'] = 0
    actual = df['actual_unit_sales'].apply(pd.np.log1p)
    temp = (predict - actual) ** 2
    weights = df['perishable'] / 4.0 + 1
    return math.sqrt(temp.dot(weights) / weights.sum())


db = config.db
resultsTable = 'test'
testQuery = "SELECT unit_sales, actual_unit_sales, perishable FROM " + resultsTable + ";"
print scoreQuery(testQuery, db)