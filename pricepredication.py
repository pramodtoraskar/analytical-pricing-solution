import datetime
import numpy as np
import pandas as pd

import statsmodels.api as sm
import matplotlib.pyplot as plt

from scipy import stats
from statsmodels.graphics.api import qqplot


# Create an Excle file object
excel_obj = pd.ExcelFile('/home/ptos/analysispro/PET_PRI_SPT_S1_M.xls')

# Parse the first sheet
df = excel_obj.parse(excel_obj.sheet_names[1])

print df

# Rename the columns
df = df.rename(columns=dict(zip(df.columns, ['DATE', 'WTI', 'Brent'])))

# Cut off the first 18 rows becasue these rowns contain NaN values for the Brent prices
# So we will have data from 1987-05-15 to 2015-08-15
df = df[350:]

df['DATE'] = pd.to_datetime(df['DATE'])
df['WTI'] = pd.to_numeric(df['WTI'])
df['Brent'] = pd.to_numeric(df['Brent'])

# Index the data set by Date
df.index = df['DATE']
# Rename the date column after re-indexing
df = df[['WTI', 'Brent']]

#df.plot()
#plt.savefig('ppdir/1_1987_to_2015.png', dpi=200)

print df.WTI

wti_arma_mod20 = sm.tsa.ARMA(df.WTI, (2, 0),).fit()

print(wti_arma_mod20.aic, wti_arma_mod20.bic, wti_arma_mod20.hqic)

print (wti_arma_mod20.params)

print sm.stats.durbin_watson(wti_arma_mod20.resid.values)

# print df.Brent

# brent_arma_mod20 = sm.tsa.ARMA(df.Brent, (2,0),).fit()
# print (brent_arma_mod20.params)
# print(brent_arma_mod20.aic, brent_arma_mod20.bic, brent_arma_mod20.hqic)

print wti_arma_mod20.resid.values

wti_resid = wti_arma_mod20.resid

stats.normaltest(wti_resid)

print wti_resid.values.squeeze()

r,q,p = sm.tsa.acf(wti_resid.values.squeeze(), qstat=True)
print r,q,p

data = np.c_[range(1,41), r[1:], q, p]
table = pd.DataFrame(data, columns=['lag', "AC", "Q", "Prob(>Q)"])
print table.set_index('lag')

print dir(wti_arma_mod20)
predict_sunspots = wti_arma_mod20.predict('2015-05-15', '2015-11-15', dynamic=True)
print predict_sunspots

# fig = plt.figure(figsize=(12,8))
# ax = fig.add_subplot(111)
# fig = qqplot(wti_resid, line='q', ax=ax, fit=True)
# fig.savefig('4_arma_sunspotsdata_normaltest.png', dpi=200)
#
# fig = plt.figure(figsize=(12,8))
# ax1 = fig.add_subplot(211)
# fig = sm.graphics.tsa.plot_acf(wti_resid.values.squeeze(), lags=40, ax=ax1)
# ax2 = fig.add_subplot(212)
# fig = sm.graphics.tsa.plot_pacf(wti_resid, lags=40, ax=ax2)
# fig.savefig('5_arma_sunspotsdata_autocorrelation.png', dpi=200)


