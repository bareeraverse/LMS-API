from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Review
from .serializers import ReviewSerializer
from courses.models import Course

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]  # listing could be AllowAny if you prefer public viewing

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        return Review.objects.filter(course_id=course_id).select_related("user")

    def perform_create(self, serializer):
        course_id = self.kwargs["course_id"]
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise ValidationError("Course not found.")

        # Optional: check enrollment before allowing review (recommended)
        # if not Enrollment.objects.filter(course=course, user=self.request.user).exists():
        #     raise PermissionDenied("You must be enrolled to review this course.")

        # Prevent duplicate (safety)
        if Review.objects.filter(course=course, user=self.request.user).exists():
            raise ValidationError("You have already reviewed this course.")

        serializer.save(user=self.request.user, course=course)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def check_object_permissions(self, request, obj):
        # allow read for authenticated users (or AllowAny if you want public)
        if request.method in ("PUT", "PATCH", "DELETE"):
            if obj.user != request.user:
                raise PermissionDenied("You can only edit or delete your own review.")
        return super().check_object_permissions(request, obj)
