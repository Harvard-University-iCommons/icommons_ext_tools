from .models_api import get_course_data
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import SingleObjectMixin
from django.http import Http404
from django.utils.translation import ugettext as _


class CourseDataMixin(SingleObjectMixin):
    """
    Retrieve a course data object based on primary key.
    """
    context_object_name = 'course_data'

    def get_object(self, queryset=None):
        # Try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        if pk is None:
            raise AttributeError("Course data detail view %s must be called with an object pk."
                                 % self.__class__.__name__)

        try:
            course_data = get_course_data(pk)
        except ObjectDoesNotExist:
            raise Http404(_("No %s found for the given key %s" % ('course_data', pk)))

        return course_data


class CourseSiteCreationAllowedMixin(CourseDataMixin):
    """
    Processes permission checks required for initiating course creation.  Being a mixin allows for a
    view to implement multiple mixins that override dispatch.
    """
    def dispatch(self, request, *args, **kwargs):
        # Retrieve the course data object and determine if user can go ahead with creation
        self.object = self.get_object()
        return super(CourseSiteCreationAllowedMixin, self).dispatch(request, *args, **kwargs)
