from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.decorators import api_view
from django.views.decorators.csrf import ensure_csrf_cookie
from operations.models import Bookmark
from operations.serializers import BookmarkDetailSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'success': True, 'username': user.username})
        return Response({'success': False, 'detail': 'Invalid credentials'}, status=400)

@api_view(['GET'])
@ensure_csrf_cookie
def get_csrf_token(request):
    return Response({'success': True})

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'success': True})

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'email': ['This field is required.']}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Always return success for security
            return Response({'detail': 'If an account with that email exists, a password reset link has been sent.'})
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password-confirm?uidb64={uid}&token={token}"
        send_mail(
            subject="Password Reset",
            message=f"Reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return Response({'detail': 'If an account with that email exists, a password reset link has been sent.'})

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')

        errors = {}
        if not uidb64:
            errors['uidb64'] = ['Missing user id.']
        if not token:
            errors['token'] = ['Missing token.']
        if not new_password1:
            errors['new_password1'] = ['New password is required.']
        if not new_password2:
            errors['new_password2'] = ['Please confirm your new password.']
        if new_password1 and new_password2 and new_password1 != new_password2:
            errors['new_password2'] = ['Passwords do not match.']
        if errors:
            return Response(errors, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({'detail': ['Invalid link.']}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'detail': ['Invalid or expired token.']}, status=400)

        user.set_password(new_password1)
        user.save()
        return Response({'detail': 'Password has been reset successfully.'})