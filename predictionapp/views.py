# Create your views here.

import re

from django.template import RequestContext
from django.shortcuts import render_to_response
from .models import SeedData, convert_xls_to_hdf5, OilType
from .forms import UploadSeedDataFileForm
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from tsdfprocessing import ProcessDataFrame


def render_graph(request):

    oil_type_obj_list = OilType.objects.all()

    # Render list of oil type.
    return render_to_response('predictionapp/render_graph.html',
                              {'oil_type_obj_list': oil_type_obj_list},
                              context_instance=RequestContext(request))

def process_df(hdf5_filename):

    oil_type_obj = OilType.objects.all()[0]

    oil_type = str(re.sub('[^A-Za-z0-9]+', '',oil_type_obj.oil_type)).lower()
    oil_of_series_count = oil_type_obj.of_series

    pdf_obj = ProcessDataFrame(hdf5_filename, oil_type, oil_of_series_count)

    pdf_obj.fetch_df()

    pdf_obj.process_seed_dataframe()

    pdf_obj.plot_intial_graph(oil_type)

    pdf_obj.prepare_peridication_sample_and_plot_graph(oil_type)

def convert_data():

    xls_filename = ''
    hdf5_filename = settings.HDF5_FILENAME
    seed_data_file_obj = SeedData.objects.all().reverse()[0]
    if seed_data_file_obj:
        xls_filename = seed_data_file_obj.doc_file.file.name

    convert_xls_to_hdf5(xls_filename, hdf5_filename)

    process_df(hdf5_filename)


def upload_seed_data(request):
    # Handle file upload
    if request.method == 'POST':

        form = UploadSeedDataFileForm(request.POST, request.FILES)

        if form.is_valid():
            new_doc = SeedData(doc_file = request.FILES['doc_file'])
            new_doc.save()

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
    return render_to_response('predictionapp/index.html')