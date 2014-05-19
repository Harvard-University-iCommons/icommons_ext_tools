from django.http import Http404
from django.core.exceptions import ImproperlyConfigured
from django.template.response import TemplateResponse


class Custom404Mixin(object):
    template_name_404 = None

    """
    Follow the model of the TemplateResponseMixin and return an array of possible templates
    to render.  Subclasses can override this method and supply some default values for
    template if a 404 template was not already provided.
    """
    def get_404_template_names(self):
        if self.template_name_404 is None:
            raise ImproperlyConfigured(
                "Custom404Mixin requires either a definition of "
                "'template_name_404' or an implementation of 'get_404_template_names()'")
        else:
            return [self.template_name_404]

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(Custom404Mixin, self).dispatch(
                request, *args, **kwargs)
        except Http404:
            return TemplateResponse(
                request=request,
                template=self.get_404_template_names(),
                status=404)
