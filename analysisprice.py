import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import statsmodels.api as sm
from statsmodels.tsa.arima_model import ARIMA

from pandas.tseries.index import date_range


def df_index(df):
    len_df = len(df.WTI)
    return pd.Index(date_range(df.Date[350].strftime("%Y-%m-%d"), periods=len_df, freq='M'))


def p_module(dta):
    print dta
    # Remove the date column after re-indexing
    dta = dta[['WTI', 'Brent']]

    dta['WTI'] = pd.to_numeric(dta['WTI'])
    dta['Brent'] = pd.to_numeric(dta['Brent'])

    return dta

# create an Excel file object
excel = pd.ExcelFile('PET_PRI_SPT_S1_M.xls')
 
# parse the first sheet
df = excel.parse(excel.sheet_names[1])
 
# rename the columns
df = df.rename(columns=dict(zip(df.columns, ['Date', 'WTI', 'Brent'])))

# cut off the first 18 rows because these rows
# contain NaN values for the Brent prices
df = df[350:]

# -----------------------------------------------------------------------------------------------------------------
# index the data set by date
df.index = df_index(df)

print df
print df.index

# Call predication module
df = p_module(df)

# -----------------------------------------------------------------------------------------------------------------

df.plot()

plt.title('Crude Oil Prices')
plt.xlabel('Year')
plt.ylabel('Price [USD]')
plt.savefig('wti_and_brent_all_data.png', dpi=200)

# -----------------------------------------------------------------------------------------------------------------

arma_mod20 = sm.tsa.ARMA(df.WTI, (2,0),).fit()

predict_sunspots = arma_mod20.predict('2015-01-31','2015-12-31', dynamic=False)
print predict_sunspots

fig, ax = plt.subplots(figsize=(12, 8))
ax = df.ix['2015-03-31':].plot(ax=ax)
fig = arma_mod20.plot_predict('2015-05-31', '2015-12-31', dynamic=False, ax=ax, plot_insample=False)

fig.savefig('arma_sunspotsdata_forecast.png', dpi=200)
