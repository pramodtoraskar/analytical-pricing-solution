import numpy as np
import pandas as pd

import statsmodels.api as sm
import matplotlib.pyplot as plt

from scipy import stats
from statsmodels.graphics.api import qqplot


def mean_forecast_err(y, yhat):
    return y.sub(yhat).mean()

print '-'*30

print 'Read statsmodels/datasets/sunspots/sunspots.csv for analysis'
print sm.datasets.sunspots.NOTE

print '-'*30

dta = sm.datasets.sunspots.load_pandas().data

print dta

print '-'*30

# Index the data set by 'YEAR'
print len(sm.tsa.datetools.dates_from_range('1700', '2008'))
print sm.tsa.datetools.dates_from_range('1700', '2008')
dta.index = pd.Index(sm.tsa.datetools.dates_from_range('1700', '2008'))

print '-'*30

# Remove the 'YEAR' column after re-indexing
del dta["YEAR"]

# Or dta = dta['SUNACTIVITY']
print dta

print '-'*30

print '-- Visualization -- '

print dta.ix[::]

dta.plot(y='SUNACTIVITY')
plt.savefig('1_arma_sunspotsdata_befor_sm.png', dpi=200)

print '='*300
print dta.values
print dta.values.squeeze()
exit()
fig = plt.figure(figsize=(12,12))

print sm.graphics.tsa.plot_acf
print sm.graphics.tsa.plot_pacf

print '--Optional--'
ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(dta.values.squeeze(), lags=40, ax=ax1)

ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(dta, lags=40, ax=ax2)

fig.savefig('2_arma_sunspotsdata.png', dpi=200)
print '='*300

print dta.SUNACTIVITY
print dta
arma_mod20 = sm.tsa.ARMA(dta, (2,0)).fit()
print (arma_mod20.params)

arma_mod30 = sm.tsa.ARMA(dta, (3,0)).fit()
print (arma_mod30.params)

arma_mod40 = sm.tsa.ARMA(dta, (4,0)).fit()
print (arma_mod40.params)

print(arma_mod20.aic, arma_mod20.bic, arma_mod20.hqic)
print(arma_mod30.aic, arma_mod30.bic, arma_mod30.hqic)
print(arma_mod40.aic, arma_mod40.bic, arma_mod40.hqic)

print arma_mod30.resid.values

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
ax = arma_mod30.resid.plot(ax=ax)
fig.savefig('3_arma_sunspotsdata_after_durbin_watson.png',dpi=200)

resid = arma_mod30.resid

print resid
print '-'*30

stats.normaltest(resid)

print stats.normaltest(resid)

print '-'*30

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
fig = qqplot(resid, line='q', ax=ax, fit=True)
fig.savefig('4_arma_sunspotsdata_normaltest.png', dpi=200)

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(resid.values.squeeze(), lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(resid, lags=40, ax=ax2)
fig.savefig('5_arma_sunspotsdata_autocorrelation.png', dpi=200)

print '-'*30

r,q,p = sm.tsa.acf(resid.values.squeeze(), qstat=True)
print r,q,p


print range(1,41)
print r[1:]
print q
print p

data = np.c_[range(1,41), r[1:],q,p]

print '-'*30
print data

table = pd.DataFrame(data, columns=['lag','AC', 'Q', 'Prob(>Q)'])
print(table.set_index('lag'))

print 'So far we dealing with 2008 year.. Let predict data till 2012'
print '-----------------------------------------------------------------'
print type(arma_mod30)
predict_sunspots = arma_mod30.predict('1990', '2012', dynamic=True)
print predict_sunspots

fig, ax = plt.subplots(figsize=(12, 8))
ax = dta.ix['1950':].plot(ax=ax)
fig = arma_mod30.plot_predict('1990', '2012', dynamic=True, ax=ax, plot_insample=False)

fig.savefig('6_arma_sunspotsdata_forecast.png', dpi=200)

print mean_forecast_err(dta.SUNACTIVITY, predict_sunspots)
