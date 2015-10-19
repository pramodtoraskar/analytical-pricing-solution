import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import statsmodels.api as sm
from statsmodels.tsa.arima_model import ARIMA

from pandas.tseries.index import date_range

import sqlalchemy, sqlalchemy.orm

# Create your views here.

engine = sqlalchemy.create_engine('sqlite:///db.sqlite3')

def parse_df():
    # create an Excel file object
    excel = pd.ExcelFile('/home/ptoraskar/aps-working/analyticalsolution/inputdata/PET_PRI_SPT_S1_M.xls')

    df = excel.parse(excel.sheet_names[0])

    with engine.connect() as conn, conn.begin():
        df['Unnamed: 2'][4:9].to_sql('tbl_oil_type1', engine)
        types_of_oil = pd.read_sql_table('tbl_oil_type1', conn)

    print(types_of_oil)
    return

    # parse the first sheet

    print(excel.sheet_names)
    for i in excel.sheet_names:
        print(i)

    #print df
    #print df.index
    #print df.columns
    print
    return

    df = excel.parse(excel.sheet_names[1])

    # rename the columns
    df = df.rename(columns=dict(zip(df.columns, ['Date', 'WTI', 'Brent'])))

    # cut off the first 18 rows because these rows
    # contain NaN values for the Brent prices
    df = df[350:]

    with engine.connect() as conn, conn.begin():
        df.to_sql('data', engine)
        data = pd.read_sql_table('data', conn)

    print(data)

if __name__ == '__main__':
    parse_df()