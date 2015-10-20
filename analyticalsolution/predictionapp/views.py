import re
import pandas as pd
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from .models import SeedData, convert_xls_to_hdf5, OilType
from .forms import UploadSeedDataFileForm


def process_df(hdf5_filename):

    oil_type_obj = OilType.objects.get(pk=1)

    store = pd.HDFStore(hdf5_filename)

    oil_type = str(re.sub('[^A-Za-z0-9]+', '',oil_type_obj.oil_type)).lower()
    if oil_type_obj.of_series == 1:
        oil_type = '{0}/{1}'.format('data_single_group',oil_type)
    else:
        oil_type = '{0}/{1}'.format('data_mul_group',oil_type)

    df = store[oil_type]

    return df


def convert_data():
    xls_filename = ''
    hdf5_filename = settings.HDF5_FILENAME
    seed_data_file_obj = SeedData.objects.all()[0]
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


# if __name__ == '__main__':
#     process_df('/home/ptoraskar/aps-working/analyticalsolution'
#                '/analyticalsolution/database/oil_production1.h5')