from django import forms


class UploadSeedDataFileForm(forms.Form):
    doc_file = forms.FileField(label='Select a file',)