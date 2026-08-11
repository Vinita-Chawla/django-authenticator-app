from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, verifyAccountSerializer, LogoutSerializer
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .emails import *
from .utils.response import CustomResponse
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class RegisterView(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = RegisterSerializer(data = data)
            if serializer.is_valid():
                serializer.save()
                send_otp_via_email(serializer.data['email'])
                return CustomResponse.success(
                    message="Registration successful! Please check email",
                    data=serializer.data,
                    status_code=status.HTTP_200_OK
                )

            return CustomResponse.validation_error(
                message="Registration failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(e)
            return CustomResponse.error(
                message="An unexpected error occurred",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyAccountView(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = verifyAccountSerializer(data = data)
            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']
                user = User.objects.filter(email=email)
                if not user.exists():
                    return CustomResponse.not_found(
                        message="Invalid user",
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                if not user[0].otp == otp:
                    return CustomResponse.validation_error(
                        message="Invalid OTP",
                        errors={"otp": "Invalid OTP"},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                user = user.first()
                user.is_verified = True
                user.save()
                return CustomResponse.success(
                    message="OTP Verified!",
                    data=serializer.data,
                    status_code=status.HTTP_200_OK
                )


            return CustomResponse.validation_error(
                message="Verification failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            ) 

        except Exception as e:
            print(e)
            return CustomResponse.error(
                message="An unexpected error occurred",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            # Validate request data
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
    
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
    
            # Since USERNAME_FIELD = "email",
            # authenticate still expects the parameter name "username"
            user = authenticate(
                username=email,
                password=password
            )
    
            if user is None:
                return CustomResponse.unauthorized(
                    message="Invalid email or password",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
    
            refresh = RefreshToken.for_user(user)
    
            response_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            }
    
            return CustomResponse.success(
                message="Login Successful",
                data=response_data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)
            return CustomResponse.error(
                message="An unexpected error occurred",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    def post(self, request):
        try:
            serializer = LogoutSerializer(data=request.data)

            if not serializer.is_valid():
                return CustomResponse.validation_error(
                    message="Logout failed",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            refresh_token = serializer.validated_data["refresh"]

            token = RefreshToken(refresh_token)
            token.blacklist()

            return CustomResponse.success(
                message="Logout Successful",
                data=None,
                status_code=status.HTTP_200_OK
            )

        except TokenError:
            return CustomResponse.validation_error(
                message="Invalid or expired refresh token",
                errors={"refresh": "Invalid or expired refresh token"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print(e)
            return CustomResponse.error(
                message="An unexpected error occurred",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

