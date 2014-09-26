from icommons_common.models import CourseInstance


class CourseData(CourseInstance):
    class Meta:
        proxy = True

    def account_id(self):
        if self.course.course_groups.count() > 0:
            return 'coursegroup:%d' % self.course.course_groups.all()[0].pk
        elif self.course.departments.count() > 0:
            return 'dept:%d' % self.course.departments.all()[0].pk
        else:
            return 'school:%s' % self.course.school.school_id

    def course_code(self):
        if self.short_title:
            return self.short_title
        elif self.course.registrar_code_display:
            return self.course.registrar_code_display
        else:
            return self.course.registrar_code

    def course_name(self):
        cname = self.title or self.course_code()
        if self.sub_title:
            cname += ': %s' % self.sub_title
        return cname

    def meta_term_id(self):
        return self.term.meta_term_id()

    def main_section_name(self):
        return '%s %s' % (self.course.school.pk.upper(), self.course_code())

