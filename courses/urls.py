from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('my-courses', views.my_courses, name='my_courses'),
    path('add-course/', views.add_course, name='add_course'),
path('my-created-courses/', views.my_created_courses, name='my_created_courses'),
 path('search/', views.search, name='search'),
 path('instructor-stats/', views.instructor_stats, name='instructor_stats'),
path('add-lesson/<slug:slug>/', views.add_lesson, name='add_lesson'),
    path('learning/<slug:slug>/', views.learning_page, name='learning_page'),
path('learning/<slug:course_slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('edit-course/<slug:slug>/', views.edit_course, name='edit_course'),
path('delete-course/<slug:slug>/', views.delete_course, name='delete_course'),
path('edit-lesson/<int:lesson_id>/', views.edit_lesson, name='edit_lesson'),
path('delete-lesson/<int:lesson_id>/', views.delete_lesson, name='delete_lesson'),
   
    
]