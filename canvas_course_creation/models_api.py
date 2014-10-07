from .models import SISCourseData


def get_course_data(course_sis_id):
    """
    Returns an instance of the SISCourseData class for the given
    course sis id.  Will raise either an ObjectDoesNotExist exception
    if the id does not map to an instance or a MultipleObjectsReturned
    exception if multiple instances match the input id.
    """
    return SISCourseData.objects.select_related('course').get(pk=course_sis_id)
