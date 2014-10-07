from icommons_common.models import CourseInstance


class SISCourseDataMixin(object):
    """
    Extends an SIS-fed CourseInstance object with methods and properties needed for course site
    creation in an extenal LMS.  Designed as a mixin to make unit testing easier.
    """
    @property
    def sis_account_id(self):
        """
        Derives an sis_account_id for this course.  Repeated calls will return the previously
        calculated value.
        :returns: formatted string
        """
        if not hasattr(self, '_sis_account_id'):
            if self.course.course_groups.count() > 0:
                self._sis_account_id = 'coursegroup:%d' % self.course.course_groups.first().pk
            elif self.course.departments.count() > 0:
                self._sis_account_id = 'dept:%d' % self.course.departments.first().pk
            else:
                self._sis_account_id = 'school:%s' % self.course.school_id
        return self._sis_account_id

    @property
    def course_code(self):
        """
        Derives the course code for this course.  Repeated calls will return the previously
        calculated value.
        :returns: string
        """
        if not hasattr(self, '_course_code'):
            if self.short_title:
                self._course_code = self.short_title
            elif self.course.registrar_code_display:
                self._course_code = self.course.registrar_code_display
            else:
                self._course_code = self.course.registrar_code
        return self._course_code

    @property
    def course_name(self):
        """
        Derives the course name for this course.  Appends the sub_title field to the name if :
        present.
        :returns: formatted string
        """
        if not hasattr(self, '_course_name'):
            cname = self.title or self.course_code
            if self.sub_title:
                cname += ': %s' % self.sub_title
            self._course_name = cname
        return self._course_name

    @property
    def sis_term_id(self):
        """
        Calculates and returns the sis_term_id for this course.  Repeated calls will return the
        previously calculated value.
        :returns: formatted string or None
        """
        if not hasattr(self, '_sis_term_id'):
            self._sis_term_id = self.term.meta_term_id()
        return self._sis_term_id

    def primary_section_name(self):
        """
        Derives the name of the primary (main) section for this course.
        :returns: formatted string
        """
        return '%s %s' % (self.course.school_id.upper(), self.course_code)


class SISCourseData(CourseInstance, SISCourseDataMixin):
    """
    Database-backed SIS course information that implements mixin.
    """
    class Meta:
        proxy = True
