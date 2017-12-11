import sqlite3
import config

db = config.db

trainTable = config.trainTable
itemsTable = config.itemsTable
storesTable = config.storesTable
transactionsTable = config.transactionsTable
testTable = config.testTable
smallTrainTable = config.smallTrainTable
resultsTable = "test"

viewName = "results_view"

results_cols = ["id", "perishable", "actual_unit_sales", "unit_sales"]
input_cols = ["date", "store_nbr", "item_nbr", "onpromotion"]
items_cols = ["class", "family"]

view_query = "CREATE VIEW " + viewName + " AS SELECT"
for col in input_cols:
    view_query = view_query + " " + smallTrainTable + "." + col + ","
for col in results_cols:
    view_query = view_query + " " + resultsTable + "." + col + ","
for col in items_cols:
    view_query = view_query + " " + itemsTable + "." + col + ","
view_query = view_query[0:-1]
view_query = view_query + " FROM " + resultsTable
view_query = view_query + " INNER JOIN " + smallTrainTable
view_query = view_query + " ON " + resultsTable + ".id = " + smallTrainTable + ".id"
view_query = view_query + " INNER JOIN " + itemsTable
view_query = view_query + " ON " + itemsTable + ".item_nbr = " + smallTrainTable + ".item_nbr"

conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute(view_query)
