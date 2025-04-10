
# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    AdminLoginView,
    UserListAPIView,
    UserDeleteAPIView,
    UserProfileUpdateAPIView,
    UserDetailAPIView,
    SubscriptionPlanDetailAPIView,
    SubscriptionPlanListCreateAPIView,


)

urlpatterns = [
    # Token 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # http://127.0.0.1:8000/user/token/
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # http://127.0.0.1:8000/user/token/refresh/

    # User Registration & Authentication
    path('register/', RegisterView.as_view(), name='register'),  # http://127.0.0.1:8000/user/register/
    path('login/', LoginView.as_view(), name='login'),           # http://127.0.0.1:8000/user/login/
    path('edit-user/', UserProfileUpdateAPIView.as_view(), name='edit-user'), #http://127.0.0.1:8000/user/edit-user/
    path("profile/", UserDetailAPIView.as_view(), name="user-profile"),  ## http://127.0.0.1:8000/user/profile/
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),  # http://127.0.0.1:8000/user/admin-login/
    
    # User Management (Admin Only)
    path('list/', UserListAPIView.as_view(), name='user-list'),  # List all users (Admin Only)  http://127.0.0.1:8000/user/list/
    path('delete/<str:user_id>/', UserDeleteAPIView.as_view(), name='user-delete'),  # Delete a user (Admin Only)  http://127.0.0.1:8000/user/delete/1/
     
    # SUbscription plan
    path('subscriptions/', SubscriptionPlanListCreateAPIView.as_view(), name='subscription-list-create'),
    path('subscriptions/<int:pk>/', SubscriptionPlanDetailAPIView.as_view(), name='subscription-detail'),


    # path('add', add_user)
]

