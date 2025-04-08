# accounts/serializers.py
from rest_framework import serializers
from .models import CustomUser
from django.conf import settings
# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ('id', 'username', 'email', 'password')
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }

#     def create(self, validated_data):
#         user = CustomUser.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         return user
# from rest_framework import serializers
# from .models import CustomUser,SubscriptionPlan

# class RegisterSerializer(serializers.ModelSerializer):
#     is_superuser = serializers.BooleanField(default=False)  # Allow superuser creation

#     class Meta:
#         model = CustomUser
#         fields = ('id', 'username', 'email', 'password', 'is_superuser')
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }

#     def create(self, validated_data):
#         is_superuser = validated_data.pop('is_superuser', False)  # Extract superuser flag

#         user = CustomUser.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )

#         if is_superuser:
#             user.is_superuser = True
#             user.is_staff = True  # Required to access Django admin
#             user.save()

#         return user

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ('id', 'username', 'email', 'is_superuser')

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'full_name', 'dob', 'gender', 'bio']
 
from rest_framework import serializers
from .models import CustomUser,SubscriptionPlan
from django.conf import settings
# class RegisterSerializer(serializers.ModelSerializer):
#     is_superuser = serializers.BooleanField(default=False)  # Allow superuser creation

#     class Meta:
#         model = CustomUser
#         fields = ('id', 'username', 'email', 'password', 'is_superuser')
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }

#     def create(self, validated_data):
#         is_superuser = validated_data.pop('is_superuser', False)  # Extract superuser flag

#         user = CustomUser.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )

#         if is_superuser:
#             user.is_superuser = True
#             user.is_staff = True  # Required to access Django admin
#             user.save()

#         return user
from rest_framework import serializers
from .models import CustomUser
from django.core.exceptions import ValidationError

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)  # Password should be write_only
    is_superuser = serializers.BooleanField(default=False)
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'is_superuser')

    def create(self, validated_data):
        is_superuser = validated_data.pop('is_superuser', False)

        # Create the user manually for MongoEngine (no `create_user` method)
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()  # Save the user to the database

        # Assign superuser privileges if requested
        if is_superuser:
            user.is_superuser = True
            user.is_staff = True  # Required to access Django admin
            user.save()

        return user


class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    plan_name = serializers.CharField(source="plan.name", read_only=True)  # Fetch plan name dynamically
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    end_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    profile_image_url = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "dob",
            "gender",
            "bio",
            'profile_image_url',
            "is_active",
            "plan_name",
            "price",
            "is_active_subscription",
            "start_date",
            "end_date",
            "stripe_price_id",
            "stripe_subscription_id",
            "created_at",
        ]
    def get_profile_image_url(self, obj):
        """Return the full URL of the profile image, handling cases where request is None"""
        request = self.context.get("request")
        if obj.profile_image:
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return settings.MEDIA_URL + obj.profile_image.url  # Fallback if no request
        return None  # No image uploaded
    
# ✅ Subscription Plan Serializer (Handles Plans Like Monthly, Yearly)
class SubscriptionPlanSerializer(serializers.Serializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'stripe_price_id', 'price', 'duration', 'description']


class StripeSubscriptionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    plan_id = serializers.IntegerField()

    def validate_plan_id(self, value):
        try:
            plan = SubscriptionPlan.objects.get(id=value)
            return plan
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid subscription plan selected.")