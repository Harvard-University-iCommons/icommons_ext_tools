from django import forms
from qualtrics_link import util


class SpoofForm(forms.Form):
    huid = forms.CharField(max_length=15, required=False)


class QualtricsUserAdminForm(forms.Form):
    division = forms.ChoiceField(choices=util.DIVISION_CHOICES)
    role = forms.ChoiceField(choices=util.ROLE_CHOICES)
    manually_updated = forms.ChoiceField(choices=(('True', 'True'), ('False', 'False')))

