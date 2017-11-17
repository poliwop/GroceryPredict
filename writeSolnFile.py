import sqlite3
import pandas as pd
import config
db = config.db
dataPath = config.outputPath
outputName = 'DOWWeightByStore'
resultsTable = "DOWWeightByStore"

conn = sqlite3.connect(db)

df = pd.read_sql_query("select id, unit_sales from " + resultsTable + ";", conn)
df[['id','unit_sales']].to_csv(dataPath + outputName + '.csv.gz', index=False, float_format='%.3f', compression='gzip')

conn.close()