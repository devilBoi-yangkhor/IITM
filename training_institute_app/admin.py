from django.contrib import admin
from .models import Role, User, Department, CourseCategory, Course, Enrollment, CourseLecturer, ContactInquiry

# Just register everything simply
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Department)
admin.site.register(CourseCategory)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(CourseLecturer)
admin.site.register(ContactInquiry)