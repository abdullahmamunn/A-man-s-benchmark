from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserSettings
from .time import DEFAULT_TIMEZONE


def account_payload(user):
    settings_obj, _ = UserSettings.objects.get_or_create(
        user=user,
        defaults={'timezone': DEFAULT_TIMEZONE},
    )
    return {
        'authenticated': True,
        'email': user.email,
        'student_name': settings_obj.student_name,
        'timezone': settings_obj.timezone,
    }


@method_decorator(ensure_csrf_cookie, name='dispatch')
class MeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'authenticated': False})
        return Response(account_payload(request.user))


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        name = (request.data.get('student_name') or '').strip()
        timezone_name = (request.data.get('timezone') or DEFAULT_TIMEZONE).strip() or DEFAULT_TIMEZONE
        try:
            ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            timezone_name = DEFAULT_TIMEZONE
        if not email or '@' not in email or email.startswith('@') or email.endswith('@'):
            return Response({'email': ['Enter the email you will sign in with.']}, status=400)
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            return Response({'email': ['An account with this email already exists.']}, status=400)
        try:
            validate_password(password, user=User(username=email, email=email))
        except ValidationError as exc:
            return Response({'password': list(exc.messages)}, status=400)
        with transaction.atomic():
            user = User.objects.create_user(username=email, email=email, password=password)
            UserSettings.objects.create(
                user=user,
                student_name=name or email.split('@')[0],
                timezone=timezone_name,
            )
        login(request, user)
        return Response(account_payload(user), status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({'detail': 'Email or password is incorrect.'}, status=400)
        login(request, user)
        return Response(account_payload(user))


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'authenticated': False})
