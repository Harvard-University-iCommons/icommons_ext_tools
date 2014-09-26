from .models import CourseData


def get_course_data(course_sis_id):
    """
    Returns an instance of the CourseData class for the given
    course sis id.  Will raise either an ObjectDoesNotExist exception
    if the id does not map to an instance or a MultipleObjectsReturned
    exception if multiple instances match the input id.
    """
    return CourseData.objects.select_related('course'). \
        prefetch_related('course__course_groups', 'course__departments'). \
        get(pk=course_sis_id)
