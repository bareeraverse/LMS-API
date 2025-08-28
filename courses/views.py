from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.generics import ListAPIView

from rest_framework.exceptions import PermissionDenied
from .models import Course, Module, Lesson,Quiz,Question,QuixAttempt,Answer
from .serializers import CourseSerializer, ModuleSerializer,LessonSerializer, QuizSerializer,QuestionSerializer
from .permissions import IsCourseTeacherOrReadOnly
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "admin":
            teacher = self.request.data.get("teacher")
            if teacher:
                serializer.save(teacher_id=teacher)
            else:
                raise ValueError("Admin must provide a teacher id")
        # Agar teacher hai to apne naam se hi banega
        elif user.role == "teacher":
            serializer.save(teacher=user)
        else:
            raise PermissionError("Only Admin or Teacher can create courses")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        user = request.user

        if user.role != "Student":
            return Response({"detail": "Only students can enroll."}, status=status.HTTP_403_FORBIDDEN)

        course.students.add(user)
        return Response({"detail": "Enrolled successfully."})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unenroll(self, request, pk=None):
        course = self.get_object()
        user = request.user

        if user.role != "Student":
            return Response({"detail": "Only students can unenroll."}, status=status.HTTP_403_FORBIDDEN)

        course.students.remove(user)
        return Response({"detail": "Unenrolled successfully."})

class ModuleListCreateView(generics.ListCreateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


    def get_queryset(self):
        return Module.objects.filter(course_id=self.kwargs['course_id']).order_by('order', 'id')

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        if self.request.user != course.teacher:
            raise PermissionDenied("Only the course's teacher can add modules.")
        serializer.save(course=course)

class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]

class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Lesson.objects.filter(module_id=self.kwargs['module_id']).order_by('order', 'id')

    def perform_create(self, serializer):
        module = get_object_or_404(Module, pk=self.kwargs['module_id'])
        if self.request.user != module.course.teacher:
            raise PermissionDenied("Only the course's teacher can add lessons.")
        serializer.save(module=module)
class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]

class StudentEnrollmentListView(ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student_id = self.kwargs["student_id"]
        user = self.request.user

        if user.id != student_id and user.role.lower() != "admin":
            raise PermissionDenied("You cannot view other students' enrollments.")

        return Course.objects.filter(students__id=student_id).order_by("id")
    

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        user = request.user
        answers_data = request.data.get('answers', [])

        if not answers_data:
            return Response({"detail": "No answers submitted."}, status=status.HTTP_400_BAD_REQUEST)

        attempt = QuixAttempt.objects.create(user=user, quiz=quiz)
        score = 0

        for ans_data in answers_data:
            question_id = ans_data.get('question')
            selected_option = ans_data.get('selected_option')

            question = quiz.questions.filter(id=question_id).first()
            if not question:
                continue

            # Save Answer
            Answer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option
            )

            # Check if correct
            if selected_option and selected_option.upper() == question.correct_option.upper():
                score += 1

        attempt.score = score
        attempt.save()

        return Response({"detail": "Quiz submitted successfully.", "score": score})

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def results(self, request, pk=None):
        quiz = self.get_object()
        user = request.user

        attempt = QuixAttempt.objects.filter(user=user, quiz=quiz).order_by('-completed_at').first()
        if not attempt:
            return Response({"detail": "No attempt found."}, status=status.HTTP_404_NOT_FOUND)

        answers_detail = []
        for ans in attempt.answers.all():
            answers_detail.append({
                "question": ans.question.text,
                "selected_option": ans.selected_option,
                "correct_option": ans.question.correct_option
            })

        return Response({
            "quiz": quiz.title,
            "score": attempt.score,
            "answers": answers_detail
        })

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
