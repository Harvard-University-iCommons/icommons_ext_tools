from django import forms


class SpoofForm(forms.Form):
    huid = forms.CharField(max_length=15, required=False)
