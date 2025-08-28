from rest_framework import serializers
from .models import Course, Module, Lesson, Quiz, Question,QuixAttempt,Answer, LessonProgress
from django.contrib.auth import get_user_model

User = get_user_model()

class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="teacher"),  # sirf teachers allowed
        required=False
    )

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'students', 'created_at']
        read_only_fields = ['students', 'created_at']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Module
        fields = ['id', 'course','title','description', 'order','created_at','updated_at']
        read_only_fields = ['course','created_at','updated_at']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'module', 'title', 'content', 'video_url', 'order', 'created_at', 'updated_at']
        read_only_fields= ['module', 'created_at', 'updated_at']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)  # 👈 yeh add karo

    class Meta:
        model=Quiz
        fields='__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['question', 'selected_option']

class QuixAttemptSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = QuixAttempt
        fields = ['id', 'user', 'quiz', 'score', 'completed_at', 'answers']

class CourseProgressSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    progress_percent = serializers.FloatField()