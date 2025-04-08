
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
    create_checkout_session, 
    payment_success,
    UserDetailAPIView,
    create_checkout_session,
    payment_success,
    cancel_subscription,
    check_subscription_status,
    stripe_webhook,

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
    path('delete/<int:user_id>/', UserDeleteAPIView.as_view(), name='user-delete'),  # Delete a user (Admin Only)  http://127.0.0.1:8000/user/delete/1/
     
     # SUbscription
    path("create-checkout-session/", create_checkout_session, name="create_checkout_session"),
    path("payment-success/", payment_success, name="payment_success"),
    path("cancel-subscription/", cancel_subscription, name="cancel_subscription"),
    path("check-subscription-status/", check_subscription_status, name="check_subscription_status"),
    path("stripe-webhook/", stripe_webhook, name="stripe_webhook"),

    # path('add', add_user)
]

