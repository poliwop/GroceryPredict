import pandas as pd

def cleanTrainSet(train):
    print "transforming data"
    train.loc[(train.unit_sales<0),'unit_sales'] = 0 # eliminate negatives
    train['unit_sales'] =  train['unit_sales'].apply(pd.np.log1p) #logarithm conversion
    train['date'] = pd.to_datetime(train['date'])
    return train

def imputeTrainSet(train, dateList = None, itemList = None):
    print "creating records"
    u_dates = train.date.unique()
    u_stores = train.store_nbr.unique()
    u_items = train.item_nbr.unique()
    if dateList is not None:
        u_dates = dateList
    if itemList is not None:
        u_items = itemList


    train.set_index(["date", "store_nbr", "item_nbr"], inplace=True)

    print train
    print u_stores
    print u_dates
    print u_items
    train = train.reindex(
        pd.MultiIndex.from_product(
            (u_dates, u_stores, u_items),
            names=["date", "store_nbr", "item_nbr"]
        )
    )
    del u_dates, u_stores, u_items

    return train

def fillNans(train):

    print "Filling NaNs"
    # Fill NaNs
    train.loc[:, "unit_sales"].fillna(0, inplace=True)
    if 'id' in train.columns:
        train.loc[:, "id"].fillna(0, inplace=True)
    train.reset_index(inplace=True) # reset index and restoring unique columns

    return train

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