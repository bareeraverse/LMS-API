from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationSerializer

# List user notifications
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


# Create notification (for admin/teacher)
class NotificationCreateView(generics.CreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]  # only admin/teacher

# Delete notification
class NotificationDeleteView(generics.DestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]
