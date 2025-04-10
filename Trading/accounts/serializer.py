# accounts/serializers.py
from .models import CustomUser,SubscriptionPlan
from django.conf import settings
from rest_framework import serializers
from .models import CustomUser
from django.core.exceptions import ValidationError
from bson.objectid import ObjectId

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
    id = serializers.CharField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField(required=False, allow_null=True)
    dob = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_null=True)
    profile_image_url = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    plan_name = serializers.CharField(source="plan.name", read_only=True, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    is_active_subscription = serializers.BooleanField()
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    end_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    stripe_price_id = serializers.CharField(required=False, allow_null=True)
    stripe_subscription_id = serializers.CharField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)

    # def get_profile_image_url(self, obj):
    #     request = self.context.get("request")
    #     if obj.profile_image:
    #         if request:
    #             return request.build_absolute_uri(obj.profile_image.url)
    #         return settings.MEDIA_URL + obj.profile_image.url
    #     return None
    def get_profile_image_url(self, obj):
        request = self.context.get("request")
        try:
            if obj.profile_image and hasattr(obj.profile_image, 'url'):
                if request:
                    return request.build_absolute_uri(obj.profile_image.url)
                return settings.MEDIA_URL + obj.profile_image.url
        except Exception:
            return None
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Ensure ID is always a string
        ret['id'] = str(instance.id)
        return ret

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        # Convert string ID to ObjectId if present
        if 'id' in ret and isinstance(ret['id'], str):
            try:
                ret['id'] = ObjectId(ret['id'])
            except:
                pass
        return ret

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