import pandas as pd
import sqlite3
from datetime import timedelta


def MovingAverages(train = None, test = None):

    db = 'GroceryPredict.db'
    conn = sqlite3.connect(db)

    if not isinstance(train, pd.DataFrame):
        raise NameError("No training DF")

    # Load test
    if not isinstance(test, pd.DataFrame):
        raise NameError("No testing DF")


    train.loc[(train.unit_sales<0),'unit_sales'] = 0 # eliminate negatives
    train['unit_sales'] =  train['unit_sales'].apply(pd.np.log1p) #logarithm conversion
    train['date'] = pd.to_datetime(train['date'])


    # creating records for all items, in all markets on all dates
    # for correct calculation of daily unit sales averages.
    print "creating records"
    u_dates = train.date.unique()
    u_stores = train.store_nbr.unique()
    u_items = train.item_nbr.unique()
    train.set_index(["date", "store_nbr", "item_nbr"], inplace=True)
    train = train.reindex(
        pd.MultiIndex.from_product(
            (u_dates, u_stores, u_items),
            names=["date", "store_nbr", "item_nbr"]
        )
    )

    del u_dates, u_stores, u_items

    print "Obtaining Day-Of-Week Weights"
    dow = pd.read_sql_query("SELECT date, store_nbr, transactions FROM transactionsInput;", conn)
    dow['date'] = pd.to_datetime(dow['date'])
    dow['dayOfWeek'] = dow['date'].dt.dayofweek
    dowavgs = dow.groupby(['dayOfWeek', 'store_nbr'])['transactions'].sum()
    storeavgs = dowavgs.groupby(['store_nbr']).mean()
    dowavgs = dowavgs.div(storeavgs, axis='index', level='store_nbr').to_frame('dowavgs')

    print "Filling NaNs"
    # Fill NaNs
    train.loc[:, "unit_sales"].fillna(0, inplace=True)
    train.reset_index(inplace=True) # reset index and restoring unique columns
    lastdate = train.iloc[train.shape[0]-1].date

    test = test.set_index(['item_nbr', 'store_nbr'])
    test['date'] = pd.to_datetime(test['date'])
    test['dayOfWeek'] = test['date'].dt.dayofweek
    ltest = test.shape[0]

    print "Calculating moving averages"
    #Moving Averages
    for i in [3,7,14,28,56,112]:
        val='MA'+str(i)
        tmp = train[train.date>lastdate-timedelta(int(i))]
        tmp1 = tmp.groupby(['item_nbr', 'store_nbr'])['unit_sales'].mean().to_frame(val)
        test = test.join(tmp1, how='left')

    print "creating output"
    #Median of MAs
    test['unit_sales']=test.iloc[:,3:].median(axis=1)
    test.loc[:, "unit_sales"].fillna(0, inplace=True)
    test['unit_sales'] = test['unit_sales'].apply(pd.np.expm1) # restoring unit values
    test['store_nbr'] = test.index.get_level_values('store_nbr')
    test = test.join(dowavgs, on=['dayOfWeek', 'store_nbr'])
    test['unit_sales'] = test['unit_sales']*test['dowavgs']

    df = test[['id','unit_sales']]
    return df
