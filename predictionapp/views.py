# Views File - All controllers and respactive methods.

import re
import os

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response

from .models import SeedData, convert_xls_to_hdf5, OilType
from .forms import UploadSeedDataFileForm

from tsdfprocessing import ProcessDataFrame


def get_oil_type_conver_name(oil_type_obj):
    """
    This method use to convert oil description to non space and in lowercase.
    :param oil_type_obj: OilType instaces
    :return: oil_type name in lower case
    """

    oil_type = str(re.sub('[^A-Za-z0-9]+', '', oil_type_obj.oil_type)).lower()
    return oil_type


def render_graph(request):
    """
    This method use to render graph on render_graph.html page
    :param request: HTTP request
    :return: render to response
    """

    # Maintain all graph paths into define dict
    graph_dict = {}

    # Check HTTP method
    if request.method == 'GET':

        oil_id = int(request.GET.get('oil_id', 0))
        oil_type_obj = OilType.objects.get(pk=oil_id)

        # Call get_oil_type_conver_name() to get oil type name
        oil_type_name = get_oil_type_conver_name(oil_type_obj)

        all_data_graph = 'plot_graph/{0}_all_data.png'.format(oil_type_name)
        all_graph_path = os.path.join(settings.MEDIA_URL, all_data_graph)
        graph_dict['all_data_path'] = all_graph_path

        three_month_data_graph = \
            'plot_graph/{0}_3m_forecast_data.png'.format(oil_type_name)
        three_month_graph_path = os.path.join(settings.MEDIA_URL,
                                              three_month_data_graph)
        graph_dict['m3_forecast_data_path'] = three_month_graph_path

        six_month_data_graph = \
            'plot_graph/{0}_6m_forecast_data.png'.format(oil_type_name)
        six_month_graph_path = os.path.join(settings.MEDIA_URL,
                                            six_month_data_graph)
        graph_dict['m6_forecast_data_path'] = six_month_graph_path

    return render_to_response('predictionapp/render_graph.html',
                              {'graph_dict': graph_dict},
                              context_instance=RequestContext(request))

def oil_categories(request):
    """
    This method use to load oil description
    :param request:HTTP request
    :return: render to responces
    """

    # Fetch all oil type from OilType to load load_oil_categories.html with all
    # categories and render page.
    oil_type_obj_list = OilType.objects.all()

    return render_to_response('predictionapp/load_oil_categories.html',
                              {'oil_type_obj_list': oil_type_obj_list},
                              context_instance=RequestContext(request))


def process_df(hdf5_filename):
    """
    This method ues to do DataFrame processing and loading data.
    :param hdf5_filename: HDF5 db path
    :return: None
    """

    try:
        oil_type_obj_list = OilType.objects.all()
    except:
        oil_type_obj_list = []

    for oil_type_obj in oil_type_obj_list:

        # Call get_oil_type_conver_name() to get oil type name
        oil_type = get_oil_type_conver_name(oil_type_obj)

        # Get of_series count from oil_type object
        oil_of_series_count = oil_type_obj.of_series

        # Create ProcessDataFrame class object
        pdf_obj = ProcessDataFrame(hdf5_filename, oil_type, oil_of_series_count)

        # Below method use to fetch DataFream from HDF5 into pandas
        # DataFream object, Do the pre processing and send for prediction
        # method to predict samples. Onces sample are pridct plot graph.

        pdf_obj.fetch_df()

        pdf_obj.process_seed_dataframe(oil_type_obj.id)

        pdf_obj.plot_intial_graph(oil_type)

        pdf_obj.prepare_peridication_sample_and_plot_graph(oil_type)


def convert_data():
    """
    Convert seed data to HDF5 data formate
    :return: None
    """

    xls_filename = ''

    # Fetch HDF5 file path and name from django settings file.
    hdf5_filename = settings.HDF5_FILENAME

    try:
        seed_data_file_obj = SeedData.objects.all().reverse()[0]
    except:
        seed_data_file_obj = None

    if seed_data_file_obj:
        # Fetch PETROLEUM & OTHER LIQUIDS xls file path
        xls_filename = seed_data_file_obj.doc_file.file.name

    # Initiate convert_xls_to_hdf5() instace to call process_df method for
    # DataFream processing
    convert_xls_to_hdf5(xls_filename, hdf5_filename)
    process_df(hdf5_filename)


def upload_seed_data(request):
    """
    Upload Seed Data and store into seed_data directory for further analysis
    and processing
    :param request: HTTP request
    :return: render to response
    """

    # Handle file upload
    if request.method == 'POST':
        form = UploadSeedDataFileForm(request.POST, request.FILES)
        if form.is_valid():
            new_doc = SeedData(doc_file = request.FILES['doc_file'])
            new_doc.save()

            # Call conver data method to process seed data and plot graphs.
            convert_data()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('upload_seed_data'))
    else:
        form = UploadSeedDataFileForm() # A empty, unbound form

    # Render list page with the documents and the form
    return render_to_response('predictionapp/upload_seeddata.html',
                              {'form': form},
                              context_instance=RequestContext(request))

def index(request):
    """
    Index method for inital verification on live application
    :param request: HTTP request
    :return: render to response
    """

    return render_to_response('predictionapp/index.html')