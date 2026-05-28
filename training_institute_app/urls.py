from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from training_institute_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('courses/details/<int:course_id>/', views.courses_details, name='courses_details'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('enroll-course/', views.enroll_course, name='enroll_course'),
    
    #Google Account Login URLs
    path('google-login/', views.google_login_direct, name='google_login_direct'),
    path('accounts/', include('allauth.urls')),
     
    #Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    
    #master urls
    path('user-management/', views.user_management, name='user_management'),
    path('user-management/delete/', views.delete_user, name='delete_user'),
    path('role-management/', views.role_management, name='role_management'),
    path('role-management/delete/', views.delete_role, name='delete_role'),
    path('course-management/', views.course_management, name='course_management'),
    
    #Page Management URLs
    path('about-page-management/', views.about_page_management, name='about_page_management'),
    path('update-about-section/', views.update_about_section, name='update_about_section'),

]