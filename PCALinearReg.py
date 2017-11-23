import pandas as pd
import sqlite3
from datetime import timedelta
import config
import numpy as np
from sklearn.decomposition import PCA
from GroceryUtil import *

trainTable = config.trainTable
itemsTable = config.itemsTable
storesTable = config.storesTable
transactionsTable = config.transactionsTable
testTable = config.testTable


def getPCA(train):
    train = cleanTrainSet(train)
    train = imputeTrainSet(train)
    train = train.pivot_table(index = ['store_nbr', 'item_nbr'], columns='date', values = 'unit_sales')


X = np.array([[-1, -1, 1], [-2, -1, 2], [-3, -2, 1], [1, 1 ,3], [2, 1, 3], [3, 2, 1]])
pca = PCA(n_components=2)
pca.fit(X)
print(pca.explained_variance_ratio_)
#print(pca.singular_values_)
print(pca.components_)