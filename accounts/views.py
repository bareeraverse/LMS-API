from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .serializers import PassswordResetRequestSerializer, PassswordResetConfirmSerializer
from .serializers import RegisterSerializer, ProfileSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response({"detail": "invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "logged out"})
    

User = get_user_model()

# 1. Request password reset
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PassswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            return Response({"uid": uid, "token": token}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PassswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid UID"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password has been reset successfully"}, status=status.HTTP_200_OK)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer  # ya agar alag UserSerializer hai, wo use karo

    def get_permissions(self):
        # Sirf Admin full access
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'list', 'retrieve']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]