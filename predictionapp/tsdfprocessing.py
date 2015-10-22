# Utils module for DataFrame proecessing and ploting graphs for the
# sample data.

import os
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

from dateutil import relativedelta
from django.conf import settings

from .models import OilType, OilDescSourceKeyMapping


class ProcessDataFrame():
    """
    Processing DataFream class
    """

    def __init__(self, hdf5_filename, oil_type, oil_of_series_count):
        """
        Initialization method for ProcessDataFrame class.
        :param hdf5_filename: path for HDF5 db file
        :param oil_type: oil desciption/type
        :param oil_of_series_count: series cout
        :return: None
        """

        self.df = None
        self.df_len = 0
        self.hdf5_filename = hdf5_filename

        self.oil_type = oil_type
        self.of_series_count = oil_of_series_count

        self.source_keys_with_col = []
        self.fit_val = None

    def fetch_df(self):
        """
        Fetch DataFrame from HDF5 file and store it into instaces df variable
        :return: None
        """

        # Fetch DataFrame
        store = pd.HDFStore(self.hdf5_filename)

        if self.of_series_count == 1:
            oil_type = '{0}/{1}'.format('data_single_group',self.oil_type)
        elif self.of_series_count == 2:
            oil_type = '{0}/{1}'.format('data_two_group',self.oil_type)
        else:
            oil_type = '{0}/{1}'.format('data_mul_group',self.oil_type)

        # Store respactive seed data into Pandas DataFrame
        self.df = store[oil_type]

    def _df_index(self, df):
        """
        Perpare DataFream index and count DataFrame length
        :param df: Pandas DataFrame object
        :return: pandas DatetimeIndex object and DataFrame length
        """

        # Count DataFrame length
        df_len = len(df.Date)

        df_date_list =  [df_date for df_date in df.Date]

        # Get DatetimeIndex list to set as DateFrame index
        pd_index = pd.DatetimeIndex(df_date_list, freq='M')

        return pd_index, df_len


    def _data_type_conversion(self, df):
        """
        This method use to conver column value into respactive format for
        further processing
        :param df: Pandas DataFream Object
        :return: Update Pandas DataFream Object
        """

        # Loop over the DataFrame column list
        for df_column in df.columns.values:
            if df_column == 'Date':
                # Convert into Datetime format
                df['Date'] = pd.to_datetime(df['Date'])
            else:
                # Convert into Numeric format
                df[df_column] = pd.to_numeric(df[df_column])

        return df


    def _get_source_keys_list(self, oil_type_id):
        """
        Get source Keys from Seed data and set source keys along with it
        column numbers
        :param oil_type_id: Oil type table id(primery key)
        :return: None
        """

        try:
            oil_type_obj = OilType.objects.get(pk=oil_type_id)
        except:
            oil_type_obj = None

        try:
            oildesc_sourcekey_mapping_list = \
                OilDescSourceKeyMapping.objects.filter(
                    oil_desc = oil_type_obj,
                    sheet_name = oil_type_obj.sheet_name)
        except:
            oildesc_sourcekey_mapping_list = []

        for odsm_ele in oildesc_sourcekey_mapping_list:
            source_key_name = str(odsm_ele.source_key.source_key)
            self.source_keys_with_col.append([source_key_name,
                                               odsm_ele.column_number])

    def process_seed_dataframe(self, oil_type_id):
        """
        Process seed DataFrame and store into HDF5 format
        :param oil_type_id: oil type table id(primery key)
        :return: None
        """

        source_keys_list = []

        # Get get source kyes list from oil type/description
        self.get_source_keys_list(oil_type_id)

        for source_keys in self.source_keys_with_col:
            source_keys_list.insert(int(source_keys[1]), source_keys[0])

        # Append new 'Date' key for indexing
        source_keys_list.append('Date')

        # Rename DataFrame columns using newly create columns_dict
        columns_dict = dict(zip(self.df.columns, source_keys_list))

        # Rename the columns
        ps_df = self.df.rename(columns=columns_dict)

        # Cut off the all selective rows because these rows contain NaN values
        # for the prices.
        ps_df = ps_df.dropna()

        # Call data type conversion method to convert respactive column values
        ps_df = self.data_type_conversion(ps_df)

        # Index the data set by date
        df_index, self.df_len = self.df_index(ps_df)

        # Now remove 'Date' column which is not require for further
        # processing.
        del ps_df['Date']

        self.df = ps_df

        # Set DatetimeIndex as index of DataFrame
        self.df.index = df_index

        # Set Fit value which will further use for prediction steps.
        self.fit_val = source_keys_list[0]

    def plot_intial_graph(self, oil_type):
        """
        Plot intial data graph
        :param oil_type: oil type/desciption
        :return: None
        """

        graph_name = '{0}_{1}'.format(oil_type, 'all_data.png')
        graph_path = os.path.join(settings.GRAPH_STORE_PATH, graph_name)

        # Call plot method to plot graph using matplotlib lib
        self.df.plot()

        # Set title
        plt.title(oil_type)

        plt.xlabel('Year')
        plt.ylabel('Price [USD]')

        # Save graph to the graph_path
        plt.savefig(graph_path, dpi=200)

    def get_plot_dates(self, df_last_date, month_diff):
        """
        Get plotting dates
        :param df_last_date: DataFrame last record date.
        :param month_diff: Month difference count number
        :return: Next predication date, slicing index for graph plotting
        """

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

    def _get_prediction_start_date(self, last_date):
        """
        Get start date for predication from last date of DataFrame
        :param last_date: last date of DataFrame
        :return: start date for predication method
        """

        record_last_date = pd.Timestamp(last_date).date()
        start_date = record_last_date.replace(month=1).isoformat()

        return start_date

    def plot_graph(self, graph_name, arma_predict_start_date,
                   arma_predict_end_date, df_ix_date,
                   plot_predict_date, df_fit_value):
        """
        Calculate predication sample and Plot graph.
        :param graph_name: predicated sample graph path
        :param arma_predict_start_date: start date for ARMA predict method
        :param arma_predict_end_date: end date for ARMA predict method
        :param df_ix_date: slicing index of DataFrame.
        :param plot_predict_date: Plotting initial date
        :param df_fit_value: Fit Value
        :return: Nane
        """
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

        # Save graph at the respactive path.
        fig.savefig(graph_name, dpi=200)

    def prepare_peridication_sample_and_plot_graph(self, oil_type):
        """
        Prepare peridication sample
        :param oil_type: oil type/desciption detail name
        :return: Nano
        """

        # Get DataFrame late date
        df_last_date = self.df.index[-1]

        # Get start date
        arma_predict_start_date = self.get_prediction_start_date(df_last_date)

        # Plot Prediction grapg for number of months i.e. 3 and 6 from
        # settings configuration variable value.

        for prediction_month_count in settings.PREDICTION_MONTH_COUNT:

            arma_predict_end_date, df_ix_date, plot_predict_date = \
                self.get_plot_dates(df_last_date,
                                    prediction_month_count)

            fig_name = '{0}m_forecast_data.png'.format(prediction_month_count)
            graph_name = '{0}_{1}'.format(oil_type, fig_name)
            graph_path = os.path.join(settings.GRAPH_STORE_PATH, graph_name)

            # Call graph plotting method
            self.plot_graph(graph_path,
                            arma_predict_start_date,
                            arma_predict_end_date,
                            df_ix_date,
                            plot_predict_date,
                            self.fit_val)
