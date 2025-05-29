from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('modules/<int:module_pk>/', views.module_detail, name='module_detail'),
    path('assessment/<int:pk>/', views.assessment_view, name='assessment'),
    path('assessment/<int:pk>/submit/', views.submit_assessment, name='submit_assessment'),
    path('initial-assessment/', views.initial_assessment, name='initial_assessment'),
    path('assessment-result/', views.assessment_result, name='assessment_result'),
    path('module-recommendation/', views.module_recommendation, name='module_recommendation'),
]
