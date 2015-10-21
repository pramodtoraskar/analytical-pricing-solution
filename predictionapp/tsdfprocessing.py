# Create time series process views here.
import os
import pandas as pd
import statsmodels.api as sm
from pandas.tseries.index import date_range
from django.conf import settings
import matplotlib.pyplot as plt

class ProcessDataFrame():

    def __init__(self, hdf5_filename, oil_type, oil_of_series_count):

        self.hdf5_filename = hdf5_filename
        self.oil_type = oil_type
        self.of_series_count = oil_of_series_count
        self.df = None

    def fetch_df(self):

        store = pd.HDFStore(self.hdf5_filename)

        if self.of_series_count == 1:
            oil_type = '{0}/{1}'.format('data_single_group',self.oil_type)
        else:
            oil_type = '{0}/{1}'.format('data_mul_group',self.oil_type)

        self.df = store[oil_type]

    def df_index(self, df):

        len_df = len(df.WTI)

        return pd.Index(date_range(
            df.Date[int(settings.NAN_PIRCE_ROWNO_FOR_COIL)].strftime("%Y-%m"),
            periods=len_df,
            freq='M'))

    def data_type_convertion(self, df):

        df['Brent'] = pd.to_numeric(df['Brent'])
        df['WTI'] = pd.to_numeric(df['WTI'])
        df['Date'] = pd.to_datetime(df['Date'])

        return df

    def process_seed_dataframe(self):

        # rename the columns
        ps_df = self.df.rename(columns=dict(zip(self.df.columns,
                                             ['Brent', 'WTI', 'Date'])))

        # Cut off the first selective rows (number from settings
        # variable)because these rows contain NaN values for the Brent prices.

        print ps_df

        ps_df = ps_df[int(settings.NAN_PIRCE_ROWNO_FOR_COIL):]

        ps_df = self.data_type_convertion(ps_df)

        # index the data set by date
        print self.df_index(ps_df)

        ps_df.index = self.df_index(ps_df)

        print ps_df
        self.df = ps_df

    def plot_intial_graph(self, oil_type):

        graph_name = '{0}_{1}'.format(oil_type, 'all_data.png')
        graph_path = os.path.join(settings.GRAPH_STORE_PATH, graph_name)

        self.df.plot()
        plt.title('Crude Oil Prices')
        plt.xlabel('Year')
        plt.ylabel('Price [USD]')
        plt.savefig(graph_path, dpi=200)

    def prepare_peridication_sample_and_plot_graph(self, oil_type):

        graph_name = '{0}_{1}'.format(oil_type, 'forecast_data.png')
        graph_path = os.path.join(settings.GRAPH_STORE_PATH, graph_name)


        print(self.df.WTI)

        arma_mod20 = sm.tsa.ARMA(self.df.WTI, (2,0),).fit()

        predict_sunspots = arma_mod20.predict('2015-01-31',
                                              '2015-12-31',
                                              dynamic=False)

        print predict_sunspots

        fig, ax = plt.subplots(figsize=(12, 8))

        ax = self.df.ix['2015-03-31':].plot(ax=ax)

        fig = arma_mod20.plot_predict('2015-05-31',
                                      '2015-12-31',
                                      dynamic=False,
                                      ax=ax,
                                      plot_insample=False)

        fig.savefig(graph_path, dpi=200)
