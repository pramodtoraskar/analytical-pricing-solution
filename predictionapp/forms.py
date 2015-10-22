from django import forms


class UploadSeedDataFileForm(forms.Form):
    """
    Form for upload seed data document file
    """
    doc_file = forms.FileField(label='Select a file to upload data! Once '
                                     'data updad system will genrate graphs',)