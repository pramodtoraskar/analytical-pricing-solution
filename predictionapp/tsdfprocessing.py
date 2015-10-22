# Create time series process views here.
import os
import pandas as pd
import statsmodels.api as sm
from django.conf import settings
import matplotlib.pyplot as plt
from dateutil import relativedelta
from .models import OilType, OilDescSourceKeyMapping


class ProcessDataFrame():

    def __init__(self, hdf5_filename, oil_type, oil_of_series_count):

        self.hdf5_filename = hdf5_filename
        self.oil_type = oil_type
        self.of_series_count = oil_of_series_count
        self.df = None
        self.df_len = 0
        self.source_keys_with_col = []
        self.fit_val = None

    def fetch_df(self):

        store = pd.HDFStore(self.hdf5_filename)

        if self.of_series_count == 1:
            oil_type = '{0}/{1}'.format('data_single_group',self.oil_type)
        elif self.of_series_count == 2:
            oil_type = '{0}/{1}'.format('data_two_group',self.oil_type)
        else:
            oil_type = '{0}/{1}'.format('data_mul_group',self.oil_type)

        self.df = store[oil_type]

    def df_index(self, df):

        df_len = len(df.Date)

        df_date_list =  [df_date for df_date in df.Date]

        pd_index = pd.DatetimeIndex(df_date_list, freq='M')

        return pd_index, df_len


    def data_type_convertion(self, df):

        print df.columns.values

        for df_column in df.columns.values:
            print 'KKKKKKKKKKKKKKKK ', df_column

            if df_column == 'Date':
                df['Date'] = pd.to_datetime(df['Date'])
            else:
                df[df_column] = pd.to_numeric(df[df_column])

        return df


    def get_source_keys_list(self, oil_type_id):

        oil_type_obj = OilType.objects.get(pk=oil_type_id)

        oildesc_sourcekey_mapping_list = \
            OilDescSourceKeyMapping.objects.filter(
                oil_desc = oil_type_obj,
                sheet_name = oil_type_obj.sheet_name)

        for odsm_ele in oildesc_sourcekey_mapping_list:
            source_key_name = str(odsm_ele.source_key.source_key)
            self.source_keys_with_col.append([source_key_name,
                                               odsm_ele.column_number])

    def process_seed_dataframe(self, oil_type_id):

        source_keys_list = []

        self.get_source_keys_list(oil_type_id)

        for source_keys in self.source_keys_with_col:
            source_keys_list.insert(int(source_keys[1]), source_keys[0])

        source_keys_list.append('Date')

        columns_dict = dict(zip(self.df.columns, source_keys_list))

        # rename the columns
        ps_df = self.df.rename(columns=columns_dict)

        print ps_df
        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        print "oil_type_id == ",oil_type_id
        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        # Cut off the first selective rows (number from settings
        # variable)because these rows contain NaN values for the Brent prices.

        #ps_df = ps_df[np.isfinite(ps_df['Date'])]
        ps_df = ps_df.dropna()
        #ps_df = ps_df[int(settings.NAN_PIRCE_ROWNO_FOR_COIL):]

        ps_df = self.data_type_convertion(ps_df)

        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"

        # index the data set by date
        df_index, self.df_len = self.df_index(ps_df)

        del ps_df['Date']

        self.df = ps_df
        self.df.index = df_index
        self.fit_val = source_keys_list[0]


    def plot_intial_graph(self, oil_type):

        graph_name = '{0}_{1}'.format(oil_type, 'all_data.png')
        graph_path = os.path.join(settings.GRAPH_STORE_PATH, graph_name)

        self.df.plot()
        plt.title(oil_type)
        plt.xlabel('Year')
        plt.ylabel('Price [USD]')
        plt.savefig(graph_path, dpi=200)

    def get_plot_dates(self, df_last_date, month_diff):

        next_month_date = (
        pd.Timestamp(df_last_date).date() + relativedelta.relativedelta(
            months=month_diff)).isoformat()

        ix_date = (
        pd.Timestamp(df_last_date).date() - relativedelta.relativedelta(
            months=month_diff)).isoformat()

        graph_predict_date = (
        pd.Timestamp(df_last_date).date() - relativedelta.relativedelta(
            months=(month_diff -1 ))).isoformat()

        return next_month_date, ix_date, graph_predict_date

    def get_prediction_start_date(self, last_date):

        record_last_date = pd.Timestamp(last_date).date()
        start_date = record_last_date.replace(month=1).isoformat()

        return start_date

    def plot_graph(self, graph_name, arma_predict_start_date,
                   arma_predict_end_date, df_ix_date,
                   plot_predict_date, df_fit_value):

        arma_mod20 = sm.tsa.ARMA(self.df[df_fit_value], (2,0)).fit()

        predict_sunspots = arma_mod20.predict(arma_predict_start_date,
                                              arma_predict_end_date,
                                              dynamic=False)

        fig, ax = plt.subplots(figsize=(12, 8))

        ax = self.df.ix[df_ix_date:].plot(ax=ax)

        fig = arma_mod20.plot_predict(plot_predict_date,
                                      arma_predict_end_date,
                                      dynamic=False,
                                      ax=ax,
                                      plot_insample=False)

        fig.savefig(graph_name, dpi=200)

    def prepare_peridication_sample_and_plot_graph(self, oil_type):

        df_last_date = self.df.index[-1]

        arma_predict_start_date = self.get_prediction_start_date(df_last_date)


        for prediction_month_count in settings.PREDICTION_MONTH_COUNT:

            arma_predict_end_date, df_ix_date, plot_predict_date = \
                self.get_plot_dates(df_last_date,
                                    prediction_month_count)

            fig_name = '{0}m_forecast_data.png'.format(prediction_month_count)
            graph_name = '{0}_{1}'.format(oil_type, fig_name)
            graph_path = os.path.join(settings.GRAPH_STORE_PATH, graph_name)

            self.plot_graph(graph_path,
                            arma_predict_start_date,
                            arma_predict_end_date,
                            df_ix_date,
                            plot_predict_date,
                            self.fit_val)
