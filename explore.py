import pandas as pd
import sqlite3
from matplotlib import pyplot
from pandas.tools.plotting import autocorrelation_plot

def parser(x):
	return pd.datetime.strptime('190'+x, '%Y-%m')


db = 'GroceryPredict.db'

conn = sqlite3.connect(db)
train = pd.read_sql_query("select date, store_nbr, item_nbr, unit_sales from trainInput WHERE store_nbr = 1 AND item_nbr = 96995;", conn)

print "hi"

#series = read_csv('shampoo-sales.csv', header=0, parse_dates=[0], index_col=0, squeeze=True, date_parser=parser)
#autocorrelation_plot(series)
#pyplot.show()