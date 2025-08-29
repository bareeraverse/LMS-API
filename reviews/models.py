from django.db import models
from django.conf import settings
from courses.models import Course  # adjust import if your courses app name differs

class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "user"], name="unique_review_per_user_per_course")
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.course} ({self.rating})"
