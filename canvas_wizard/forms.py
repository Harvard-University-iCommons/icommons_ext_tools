from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit, Button
from crispy_forms.bootstrap import FormActions
from icommons_common.models import Template, TermCode, TemplateUser, TemplateAccount, TemplateCourseDelegates
from django.forms import ModelForm
from django.core.exceptions import ValidationError
#from datetime 
import datetime
import logging

logger = logging.getLogger(__name__)

class AddCourseDelegateForm(forms.ModelForm):
    class Meta:
        model = TemplateCourseDelegates

    course_instance_id = forms.CharField(max_length=20, widget=forms.HiddenInput())
    delegate_id = forms.CharField(max_length=20, required=True, label='Enter Delegate ID')

    def __init__(self, *args, **kwargs):
        super(AddCourseDelegateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-inline'
        #self.helper.label_class = 'col-lg-2'
        #self.helper.field_class = 'col-lg-2'
        self.helper.help_text_inline = True
        self.helper.render_unmentioned_fields = True
        self.helper.form_action = 'add_course_delegate_action'
        self.helper.form_error_title = u"There were problems with the information you submitted."
        self.helper.layout = Layout(
            Field('course_instance_id'),
            Field('delegate_id'),
            Div(
                FormActions(
                    Submit('save', 'Add Delegate', css_class='btn-primary'),
                )
                , css_class="text-box")
            )
        def clean(self):
            cleaned_data = super(AddCourseDelegateForm, self).clean()

            return cleaned_data

        def save(self, commit=True, *args, **kwargs):
            instance = super(AddCourseDelegateForm, self).save(commit=False, *args, **kwargs)
            if commit:
                instance.save()
                
            return instance

class AddUserForm(forms.ModelForm):
    class Meta:
        model = TemplateUser
        #exclude = ['date_added']
    
    TRUE = 'Y'
    FALSE = 'N'
    CHOICES = (
        (TRUE, 'True'),
        (FALSE, 'False'),
    )

    user_id = forms.CharField(max_length=20, required=True)
    sis_account_id = forms.ModelChoiceField(required=True, queryset=TemplateAccount.objects.all())
    can_manage_templates = forms.ChoiceField(choices=CHOICES)
    can_bulk_create_courses = forms.ChoiceField(choices=CHOICES)
    can_manage_users = forms.ChoiceField(choices=CHOICES)
    date_added = forms.DateTimeField(initial=datetime.datetime.now, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.help_text_inline = True
        self.helper.render_unmentioned_fields = True
        self.helper.form_action = 'add_new_user_action'
        self.helper.form_error_title = u"There were problems with the information you submitted."
        self.helper.layout = Layout(
            Field('user_id'),
            Field('sis_account_id'),
            Field('can_manage_templates'),
            Field('can_bulk_create_courses'),
            Field('can_manage_users'),
            Div(
                FormActions(
                    Submit('save', 'Save changes', css_class='btn-primary'),
                    Button('cancel', 'Cancel')
                )
                , css_class="text-box")
            )

    def clean(self):
        cleaned_data = super(AddUserForm, self).clean()

        #cleaned_data['date_added'] = datetime.datetime.now()
        #logger.debug('in clean->date_added='+date_added)

        return cleaned_data

    def save(self, commit=True, *args, **kwargs):
        instance = super(AddUserForm, self).save(commit=False, *args, **kwargs)
        #cleaned_data = self.cleaned_data
        #instance.template_id = cleaned_data['template_id']
        if commit:
            instance.save()
            
        return instance

class AddTemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        exclude = ['template_id']

    #template_id = forms.AutoField(primary_key=True)
    template_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    term = forms.ModelChoiceField(required=True, queryset=TermCode.objects.all())
    title = forms.CharField(max_length=200)
    canvas_course_id = forms.IntegerField(required=True)
    
    def __init__(self, template_id=None, *args, **kwargs):
        super(AddTemplateForm, self).__init__(*args, **kwargs)
        self._template_id = template_id
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.help_text_inline = True
        self.helper.render_unmentioned_fields = True
        self.helper.form_action = 'add_new_template_action'
        self.helper.form_error_title = u"There were problems with the information you submitted."
        self.helper.layout = Layout(
            Field('canvas_course_id'),
            Field('title'),
            Field('term'),
            Div(
                FormActions(
                    Submit('save', 'Save changes', css_class='btn-primary'),
                    Button('cancel', 'Cancel')
                )
                , css_class="text-box")
            )

    def clean(self):
        cleaned_data = super(AddTemplateForm, self).clean()
        
        cleaned_data['template_id'] = self._template_id
        #term = cleaned_data['template_term']
        #print term
        print cleaned_data['template_id']
        print cleaned_data['term']
        print cleaned_data['title']
        print cleaned_data['canvas_course_id']
        logger.debug("clean complete")

        return cleaned_data

    def save(self, commit=True, *args, **kwargs):
        instance = super(AddTemplateForm, self).save(commit=False, *args, **kwargs)
        cleaned_data = self.cleaned_data
        instance.template_id = cleaned_data['template_id']
        if commit:
            instance.save()
            
        return instance
