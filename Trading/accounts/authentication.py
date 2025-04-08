from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthenticationBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None


# accounts/authentication.py

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from mongoengine.errors import DoesNotExist
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from bson import ObjectId
from .tokens import MongoAccessToken, MongoRefreshToken
from .models import CustomUser

class MongoUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Use MongoEngine's query syntax directly
            user = CustomUser.objects(username=username).first()
            if user and user.check_password(password):
                return user
        except DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            # Convert string ID to ObjectId if needed
            if isinstance(user_id, str):
                try:
                    user_id = ObjectId(user_id)
                except:
                    pass
            # Use MongoEngine's query syntax directly
            return CustomUser.objects(id=user_id).first()
        except (DoesNotExist, ValueError):
            return None

    def get_user_permissions(self, user_obj, obj=None):
        return set()

    def get_group_permissions(self, user_obj, obj=None):
        return set()

    def get_all_permissions(self, user_obj, obj=None):
        return set()

    def has_perm(self, user_obj, perm, obj=None):
        return False

    def has_module_perms(self, user_obj, app_label):
        return False

class MongoJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
            # Convert string ID to ObjectId if needed
            if isinstance(user_id, str):
                try:
                    user_id = ObjectId(user_id)
                except:
                    pass
            # Use MongoEngine's query syntax directly
            return CustomUser.objects(id=user_id).first()
        except (DoesNotExist, ValueError):
            return None

    def get_validated_token(self, raw_token):
        """
        Returns a validated token containing the user ID as a string.
        """
        token = super().get_validated_token(raw_token)
        # Ensure the user ID is stored as a string
        token[api_settings.USER_ID_CLAIM] = str(token[api_settings.USER_ID_CLAIM])
        return token
