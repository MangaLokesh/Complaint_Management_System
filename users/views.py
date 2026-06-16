import os

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import render
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import UserProfile
from .serializers import RegisterSerializer

User = get_user_model()
 

def home(request):
    return render(request, "home.html")


def login(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


@api_view(["POST"])
@permission_classes([AllowAny])
def register_api(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.create_user(
        username=serializer.validated_data["username"],
        email=serializer.validated_data.get("email", ""),
        password=serializer.validated_data["password"]
    )

    phone_number = serializer.validated_data.get("phone_number", "").strip()
    if phone_number:
        UserProfile.objects.update_or_create(user=user, defaults={"phone_number": phone_number})

    return Response({"message": "User registered successfully ✅"}, status=201)


def _send_sms_message(phone_number, message):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        print("SMS reset link:", message)
        return True

    response = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
        data={"From": from_number, "To": phone_number, "Body": message},
        auth=(account_sid, auth_token),
        timeout=30,
    )
    response.raise_for_status()
    return True


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_sms(request):
    phone_number = request.data.get("phone_number", "").strip()
    if not phone_number:
        return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

    profile = UserProfile.objects.filter(phone_number=phone_number).select_related("user").first()
    if not profile:
        return Response({"error": "No account found for that phone number"}, status=status.HTTP_404_NOT_FOUND)

    user = profile.user
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)
    reset_link = f"{request.scheme}://{request.get_host()}/reset/{uid}/{token}/"

    try:
        _send_sms_message(phone_number, f"Reset your password here: {reset_link}")
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "Password reset link sent via SMS"}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({
        "username": request.user.username,
        "is_superuser": request.user.is_superuser
    })