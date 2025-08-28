from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.generics import ListAPIView
from django.contrib.auth import get_user_model

from rest_framework.exceptions import PermissionDenied
from .models import Course,Certificate, Module, Lesson,Quiz,Question,QuixAttempt,Answer,LessonProgress
from .serializers import CertificateSerializer,CourseSerializer, ModuleSerializer,LessonSerializer, QuizSerializer,QuestionSerializer
from .permissions import IsCourseTeacherOrReadOnly
User = get_user_model()

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

class StudentProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        user = request.user

        # Only the student themselves or admin can access
        if user.id != student_id and user.role.lower() != "admin":
            raise PermissionDenied("You cannot view other students' progress.")

        courses = Course.objects.filter(students__id=student_id)
        data = []

        for course in courses:
            total_lessons = Lesson.objects.filter(module__course=course).count()
            completed_lessons = LessonProgress.objects.filter(
                lesson__module__course=course,
                student_id=student_id,
                completed=True
            ).count()
            percent = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

            data.append({
                'course_id': course.id,
                'course_title': course.title,
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'progress_percent': round(percent, 2)
            })

        return Response(data)
    
class CourseProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        data = []

        for student in course.students.all():
            total_lessons = Lesson.objects.filter(module__course=course).count()
            completed_lessons = LessonProgress.objects.filter(
                lesson__module__course=course,
                student=student,
                completed=True
            ).count()
            percent = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

            data.append({
                'student_id': student.id,
                'student_name': student.username,
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'progress_percent': round(percent, 2)
            })

        return Response(data)
class CertificateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        user = request.user
        course = get_object_or_404(Course, pk=course_id)

        cert = Certificate.objects.filter(course=course, student=user).first()
        if not cert:
            return Response({"detail": "Certificate not found or course not completed."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CertificateSerializer(cert)
        return Response(serializer.data)

    def post(self, request, course_id):
        user = request.user
        course = get_object_or_404(Course, pk=course_id)

        # Only teacher/admin can issue certificate
        if user.role.lower() not in ['teacher', 'admin']:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        student_id = request.data.get('student_id')
        if not student_id:
            return Response({"detail": "student_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        student = get_object_or_404(User, pk=student_id)

        # Optional: check course completion
        # For now, we allow issuing directly

        certificate, created = Certificate.objects.get_or_create(course=course, student=student, issued_by=user)

        serializer = CertificateSerializer(certificate)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)