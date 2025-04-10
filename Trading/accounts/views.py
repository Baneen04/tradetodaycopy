# accounts/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.authentication import MongoJWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, get_user_model
from accounts.serializer import UserSerializer, RegisterSerializer, SubscriptionPlanSerializer, SubscriptionPlan
from django.utils.timezone import now
from rest_framework.generics import RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from mongoengine.errors import DoesNotExist
from bson import ObjectId

# from .models import CustomUser
from django.contrib.auth.hashers import check_password
# User = get_user_model()
from django.http import JsonResponse
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.hashers import make_password
from .models import CustomUser  # Import your CustomUser model
# ✅ User Registration View
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": RegisterSerializer(user, context=self.get_serializer_context()).data,
            'is_superuser': user.is_superuser, 
            "message": "User registered successfully.",
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)

# # ✅ User Login View
from mongoengine.errors import DoesNotExist  # MongoEngine exception

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)  # ✅ MongoEngine query
        except DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):  # ✅ Custom check_password
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        user.last_login = now()
        user.save()

        refresh = RefreshToken.for_user(user)  # ✅ Use custom user for JWT
        return Response({
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    
# ✅ List All Users (Only for Admins)
class UserListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = (MongoJWTAuthentication,)
    queryset = CustomUser.objects.all().order_by("-is_staff")
    serializer_class = UserSerializer

## LOgin user details
class UserDetailAPIView(RetrieveAPIView):
    """API View for fetching logged-in user details."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [MongoJWTAuthentication]
    serializer_class = UserSerializer

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user
    

# ✅ Delete a User (Only Admins Can Delete Users)
class UserDeleteAPIView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = (MongoJWTAuthentication,)

    def delete(self, request, user_id):
        try:
            # Convert the user_id from string to ObjectId
            user_id_obj = ObjectId(user_id)
            user = CustomUser.objects.get(id=user_id_obj)
            user.delete()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#update user
class UserProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [MongoJWTAuthentication]

    def put(self, request):
        user = request.user  # Authenticated MongoEngine user

        try:
            # Update fields if provided
            email = request.data.get("email")
            full_name = request.data.get("full_name")
            username = request.data.get("username")
            dob = request.data.get("dob")
            gender = request.data.get("gender")
            bio = request.data.get("bio")
            profile_image = request.FILES.get("profile_image")

            if email:
                # Check if email is already taken by another user
                existing_user = CustomUser.objects.filter(email=email).first()
                if existing_user and str(existing_user.id) != str(user.id):
                    return Response({"error": "Email already taken"}, status=status.HTTP_400_BAD_REQUEST)
                user.email = email
            if full_name:
                user.full_name = full_name
            if username:
                # Check if username is already taken by another user
                existing_user = CustomUser.objects.filter(username=username).first()
                if existing_user and str(existing_user.id) != str(user.id):
                    return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
                user.username = username
            if dob:
                user.dob = dob
            if gender:
                user.gender = gender
            if bio:
                user.bio = bio
            if profile_image:
                user.profile_image = profile_image

            user.save()
            serialized_user = UserSerializer(user).data
            # Ensure ID is properly serialized as string
            serialized_user['id'] = str(user.id)
            
            return Response({
                "message": "Profile updated successfully",
                "user": serialized_user
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ✅ Admin Login View (Now Works Properly)
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = CustomUser.objects.get(email=email)  # MongoEngine query
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):  # Custom check_password
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_superuser:
            return Response({"error": "Invalid admin credentials"}, status=status.HTTP_403_FORBIDDEN)

        user.last_login = now()
        user.save(update_fields=['last_login'])

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Admin login successful",
            "admin_status": "Superuser",
            "user_id": str(user.id),
            "email": user.email,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)

   
## Subscription plan
# ✅ List and Create Subscription Plans
class SubscriptionPlanListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: Retrieve a list of subscription plans (Open to all)
    POST: Create a new subscription plan (Admin only)
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = (MongoJWTAuthentication,)
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]  # Only authenticated users (Admins) can create plans
        return [AllowAny()]  # Everyone can view plans
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:  # Ensure only Admins can create plans
            return Response({"error": "Only admins can create subscription plans"}, status=status.HTTP_403_FORBIDDEN)
        return self.create(request, *args, **kwargs)



# ✅ Retrieve, Update, and Delete a Subscription Plan
class SubscriptionPlanDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a single subscription plan
    PUT/PATCH: Update a subscription plan (Admin only)
    DELETE: Delete a subscription plan (Admin only)
    """
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]  # Require authentication for update & delete
    authentication_classes = (MongoJWTAuthentication,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Only admins can update subscription plans"}, status=status.HTTP_403_FORBIDDEN)
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Only admins can delete subscription plans"}, status=status.HTTP_403_FORBIDDEN)
        return self.destroy(request, *args, **kwargs)
