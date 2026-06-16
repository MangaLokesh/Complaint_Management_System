from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
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
        email=serializer.validated_data["email"],
        password=serializer.validated_data["password"]
    )
    return Response({
        "message": "User registered successfully ✅"
    }, status=201)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({
        "username": request.user.username,
        "email": request.user.email,
        "is_superuser": request.user.is_superuser
    })
