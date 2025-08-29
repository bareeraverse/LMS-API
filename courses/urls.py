from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentEnrollmentListView,
    QuizViewSet,
    QuestionViewSet,
    CourseViewSet,
    ModuleListCreateView,
    ModuleDetailView,
    LessonListCreateView,
    LessonDetailView,
    StudentProgressView,       
    CourseProgressView,
    CertificateView         
)
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question') 

urlpatterns = [
    path('', include(router.urls)),
    path('courses/<int:course_id>/modules/', ModuleListCreateView.as_view(), name='module-list-create'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='module-detail'),
    path('modules/<int:module_id>/lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('students/<int:student_id>/enrollments/', StudentEnrollmentListView.as_view(), name='student-enrollments'),
    path('students/<int:student_id>/progress/', StudentProgressView.as_view(), name='student-progress'),
   
    path('courses/<int:course_id>/progress/', CourseProgressView.as_view(), name='course-progress'),
    path('courses/<int:course_id>/certificate/', CertificateView.as_view(), name='course-certificate'),

]
