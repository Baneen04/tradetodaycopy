# # accounts/models.py
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.db import models

# class CustomUserManager(BaseUserManager):
#     def create_user(self, username, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field must be set")
#         if not username:
#             raise ValueError("The Username field must be set")
#         email = self.normalize_email(email)
#         user = self.model(username=username, email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(username, email, password, **extra_fields)

# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     id = models.AutoField(primary_key=True)  # Ensure ID is explicitly defined
#     username = models.CharField(max_length=150, unique=True)  # Move up
#     email = models.EmailField(unique=True)  # Move up
#     password = models.CharField(max_length=128)  # Explicitly define password
#     last_login = models.DateTimeField(null=True, blank=True)  # Define it explicitly

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     def __str__(self):
#         return self.username


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from datetime import timedelta


# class CustomUserManager(BaseUserManager):
#     def create_user(self, username, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field must be set")
#         if not username:
#             raise ValueError("The Username field must be set")
        
#         email = self.normalize_email(email)
#         user = self.model(username=username, email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(username, email, password, **extra_fields)

# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     id = models.AutoField(primary_key=True)  # Explicit ID field
#     username = models.CharField(max_length=150, unique=True)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=128)

#     # New Profile Fields
#     full_name = models.CharField(max_length=255, blank=True, null=True)  # Optional full name
#     dob = models.DateField(blank=True, null=True)  # Date of Birth
#     gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
#     bio = models.TextField(blank=True, null=True)  # User bio

#     last_login = models.DateTimeField(null=True, blank=True)  # Explicitly define last_login

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     def __str__(self):
#         return self.username



# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.db import models
# from django.utils.timezone import now
# from django.db.models.signals import post_migrate
# from django.dispatch import receiver
# from datetime import timedelta

# # ✅ Subscription Plan Model
# class SubscriptionPlan(models.Model):
#     PLAN_TYPES = [("Monthly", "Monthly"), ("Yearly", "Yearly")]

#     name = models.CharField(max_length=100, unique=True)  # e.g., "Basic Monthly"
#     stripe_price_id = models.CharField(max_length=255, unique=True)  # Required for Stripe
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration = models.CharField(max_length=10, choices=PLAN_TYPES)  # Monthly or Yearly
#     description = models.TextField(blank=True, null=True)  # ✅ Added Description Field

#     def __str__(self):
#         return f"{self.name} - {self.duration} - ${self.price}"

# # ✅ Automatically Add Default Plans After Migration
# @receiver(post_migrate)
# def create_default_subscription_plans(sender, **kwargs):
#     if sender.name == "accounts":  # ✅ Replace with your actual Django app name
#         plans = [
#             {
#                 "name": "Basic Monthly",
#                 "price": 20,
#                 "duration": "Monthly",
#                 "stripe_price_id": "price_1XXX",
#                 "description": "Basic Monthly plan with standard features."
#             },
#             {
#                 "name": "Premium Monthly",
#                 "price": 60,
#                 "duration": "Monthly",
#                 "stripe_price_id": "price_2XXX",
#                 "description": "Premium Monthly plan with advanced features and priority support."
#             },
#             {
#                 "name": "Basic Yearly",
#                 "price": 24,
#                 "duration": "Yearly",
#                 "stripe_price_id": "price_3XXX",
#                 "description": "Basic Yearly plan with cost-saving benefits."
#             },
#             {
#                 "name": "Premium Yearly",
#                 "price": 96,
#                 "duration": "Yearly",
#                 "stripe_price_id": "price_4XXX",
#                 "description": "Premium Yearly plan with full access and VIP support."
#             },
#         ]

#         for plan in plans:
#             SubscriptionPlan.objects.get_or_create(
#                 name=plan["name"],
#                 defaults={
#                     "price": plan["price"],
#                     "duration": plan["duration"],
#                     "stripe_price_id": plan["stripe_price_id"],
#                     "description": plan["description"],  # ✅ Added description here
#                 }
#             )

#         print("✅ Default subscription plans added successfully!")


# ## User image
# def user_directory_path(instance, filename):
#     """Generate file path for user profile images inside media/<username>/"""
#     return f"{instance.username}/{filename}"  # Store in media/username/

# class CustomUserManager(BaseUserManager):
#     def create_user(self, username, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field must be set")
#         if not username:
#             raise ValueError("The Username field must be set")
        
#         email = self.normalize_email(email)
#         user = self.model(username=username, email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(username, email, password, **extra_fields)

# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     id = models.AutoField(primary_key=True)  # Explicit ID field
#     username = models.CharField(max_length=150, unique=True)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=128)

#     # Profile Fields
#     full_name = models.CharField(max_length=255, blank=True, null=True)
#     dob = models.DateField(blank=True, null=True)
#     gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
#     bio = models.TextField(blank=True, null=True)
#         # **Profile Image (Stored in DB and filesystem)**
#     profile_image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)  
#     last_login = models.DateTimeField(null=True, blank=True)

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)

#     # **Subscription Fields (Merged from UserSubscription)**
#     plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)  # Link to SubscriptionPlan
#     price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Store price
#     is_active_subscription = models.BooleanField(default=False)  # Active subscription status
#     start_date = models.DateTimeField(null=True, blank=True)  # Subscription start date
#     end_date = models.DateTimeField(null=True, blank=True)  # Subscription end date

#     stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
#     stripe_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)  # Account creation timestamp

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     def __str__(self):
#         return self.username

#     def activate_subscription(self, plan, stripe_price_id, stripe_subscription_id):
#         """Activate user subscription with given plan details."""
#         self.plan = plan
#         self.price = plan.price
#         self.is_active_subscription = True
#         self.start_date = now()
#         self.end_date = now() + timedelta(days=plan.duration_days)
#         self.stripe_price_id = stripe_price_id
#         self.stripe_subscription_id = stripe_subscription_id
#         self.save()

#     def deactivate_subscription(self):
#         """Deactivate user subscription."""
#         self.is_active_subscription = False
#         self.plan = None
#         self.price = None
#         self.start_date = None
#         self.end_date = None
#         self.stripe_price_id = None
#         self.stripe_subscription_id = None
#         self.save()

##################################################################
###################correct code
####################################################


# class SubscriptionPlan(models.Model):
#     PLAN_TYPES = [("Monthly", "Monthly"), ("Yearly", "Yearly")]

#     name = models.CharField(max_length=100, unique=True)  # e.g., "Basic Monthly"
#     stripe_price_id = models.CharField(max_length=255, blank=True, null=True) # Required for Stripe
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration = models.CharField(max_length=10, choices=PLAN_TYPES)  # Monthly or Yearly
#     description = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.name} - {self.duration} - ${self.price}"

#     @property
#     def duration_days(self):
#         """Convert plan duration into days for subscription calculations."""
#         return 30 if self.duration == "Monthly" else 365


# # ✅ Automatically Add Default Subscription Plans After Migration
# @receiver(post_migrate)
# def create_default_subscription_plans(sender, **kwargs):
#     if sender.name == "accounts":  # Replace 'accounts' with your actual Django app name
#         plans = [
#             {
#                 "name": "Basic Monthly",
#                 "price": 20,
#                 "duration": "Monthly",
#                 "description": "Basic Monthly plan with standard features."
#             },
#             {
#                 "name": "Premium Monthly",
#                 "price": 60,
#                 "duration": "Monthly",
#                 "description": "Premium Monthly plan with advanced features and priority support."
#             },
#             {
#                 "name": "Basic Yearly",
#                 "price": 24,
#                 "duration": "Yearly",
#                 "description": "Basic Yearly plan with cost-saving benefits."
#             },
#             {
#                 "name": "Premium Yearly",
#                 "price": 96,
#                 "duration": "Yearly",
#                 "description": "Premium Yearly plan with full access and VIP support."
#             },
#         ]

#         for plan in plans:
#             SubscriptionPlan.objects.get_or_create(
#                 name=plan["name"],
#                 defaults={
#                     "price": plan["price"],
#                     "duration": plan["duration"],
#                     "description": plan["description"],
#                 }
#             )

#         print("✅ Default subscription plans added successfully!")


# ## User image
# def user_directory_path(instance, filename):
#     """Generate file path for user profile images inside media/<username>/"""
#     return f"{instance.username}/{filename}"  # Store in media/username/

# class CustomUserManager(BaseUserManager):
#     def create_user(self, username, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field must be set")
#         if not username:
#             raise ValueError("The Username field must be set")
        
#         email = self.normalize_email(email)
#         user = self.model(username=username, email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(username, email, password, **extra_fields)

# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     id = models.AutoField(primary_key=True)  # Explicit ID field
#     username = models.CharField(max_length=150, unique=True)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=128)

#     # Profile Fields
#     full_name = models.CharField(max_length=255, blank=True, null=True)
#     dob = models.DateField(blank=True, null=True)
#     gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
#     bio = models.TextField(blank=True, null=True)
#         # **Profile Image (Stored in DB and filesystem)**
#     profile_image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)  
#     last_login = models.DateTimeField(null=True, blank=True)

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)

#     # **Subscription Fields (Merged from UserSubscription)**
#     plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)  # Link to SubscriptionPlan
#     price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Store price
#     is_active_subscription = models.BooleanField(default=False)  # Active subscription status
#     start_date = models.DateTimeField(null=True, blank=True)  # Subscription start date
#     end_date = models.DateTimeField(null=True, blank=True)  # Subscription end date

#     stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
#     stripe_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)  # Account creation timestamp

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     def __str__(self):
#         return self.username

#     def activate_subscription(self, plan, stripe_price_id, stripe_subscription_id):
#         """Activate user subscription with given plan details."""
#         self.plan = plan
#         self.price = plan.price
#         self.is_active_subscription = True
#         self.start_date = now()
#         self.end_date = now() + timedelta(days=plan.duration_days)
#         self.stripe_price_id = stripe_price_id
#         self.stripe_subscription_id = stripe_subscription_id
#         self.save()

#     def deactivate_subscription(self):
#         """Deactivate user subscription."""
#         self.is_active_subscription = False
#         self.plan = None
#         self.price = None
#         self.start_date = None
#         self.end_date = None
#         self.stripe_price_id = None
#         self.stripe_subscription_id = None
#         self.save()


# # ✅ Automatically update expired subscriptions
# @receiver(post_migrate)
# def update_expired_subscriptions(sender, **kwargs):
#     """Deactivate subscriptions where end_date has passed."""
#     expired_users = CustomUser.objects.filter(is_active_subscription=True, end_date__lt=now())
#     for user in expired_users:
#         user.deactivate_subscription()
#     print("✅ Expired subscriptions have been deactivated.")

from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField, DecimalField, ReferenceField, ImageField
from mongoengine.fields import DateField
from datetime import timedelta
from django.contrib.auth.hashers import check_password, make_password
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from mongoengine.queryset.visitor import Q

class SubscriptionPlan(Document):
    PLAN_TYPES = [("Monthly", "Monthly"), ("Yearly", "Yearly")]

    name = StringField(max_length=100, unique=True)
    stripe_price_id = StringField(max_length=255, blank=True, null=True)
    price = DecimalField(max_digits=10, decimal_places=2)
    duration = StringField(choices=PLAN_TYPES)
    description = StringField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.duration} - ${self.price}"

    @property
    def duration_days(self):
        """Return the duration of the subscription in days."""
        return 30 if self.duration == "Monthly" else 365


# Automatically Add Default Subscription Plans After Migration

def create_default_subscription_plans():
    if SubscriptionPlan.objects.count() == 0:  # Check if no subscription plans exist
        plans = [
            {
                "name": "Basic Monthly",
                "price": 20,
                "duration": "Monthly",
                "description": "Basic Monthly plan with standard features."
            },
            {
                "name": "Premium Monthly",
                "price": 60,
                "duration": "Monthly",
                "description": "Premium Monthly plan with advanced features and priority support."
            },
            {
                "name": "Basic Yearly",
                "price": 24,
                "duration": "Yearly",
                "description": "Basic Yearly plan with cost-saving benefits."
            },
            {
                "name": "Premium Yearly",
                "price": 96,
                "duration": "Yearly",
                "description": "Premium Yearly plan with full access and VIP support."
            },
        ]

        for plan in plans:
            # Check if the plan already exists and create it if not
            if not SubscriptionPlan.objects.filter(name=plan["name"]).first():
                SubscriptionPlan(**plan).save()  # Save the plan if it doesn't already exist

        print("✅ Default subscription plans added successfully!")

# Custom User Model

# ## User image
def user_directory_path(instance, filename):
    """Generate file path for user profile images inside media/<username>/"""
    return f"{instance.username}/{filename}"  # Store in media/username/

class CustomUser(Document):
    username = StringField(max_length=150, unique=True)
    email = EmailField(unique=True)
    password = StringField(max_length=128)

    # Profile Fields
    full_name = StringField(max_length=255, blank=True, null=True)
    dob = DateField(blank=True, null=True)
    gender = StringField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    bio = StringField(blank=True, null=True)
    profile_image = ImageField(upload_to=user_directory_path, blank=True, null=True)
    last_login = DateTimeField(null=True, blank=True)

    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    # Subscription Fields
    plan = ReferenceField(SubscriptionPlan, null=True, blank=True)
    price = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active_subscription = BooleanField(default=False)
    start_date = DateTimeField(null=True, blank=True)
    end_date = DateTimeField(null=True, blank=True)

    stripe_price_id = StringField(max_length=255, blank=True, null=True)
    stripe_subscription_id = StringField(max_length=255, null=True, blank=True)

    created_at = DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def activate_subscription(self, plan, stripe_price_id, stripe_subscription_id):
        """Activate user subscription with given plan details."""
        self.plan = plan
        self.price = plan.price
        self.is_active_subscription = True
        self.start_date = now()
        self.end_date = now() + timedelta(days=plan.duration_days)
        self.stripe_price_id = stripe_price_id
        self.stripe_subscription_id = stripe_subscription_id
        self.save()

    def deactivate_subscription(self):
        self.is_active_subscription = False
        self.plan = None
        self.price = None
        self.start_date = None
        self.end_date = None
        self.stripe_price_id = None
        self.stripe_subscription_id = None
        self.save()

    @classmethod
    def update_expired_subscriptions(cls):
        expired_users = cls.objects.filter(is_active_subscription=True, end_date__lt=now())
        for user in expired_users:
            user.deactivate_subscription()
        print("✅ Expired subscriptions deactivated!")

    # Add Django authentication interface methods
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_username(self):
        return self.username

    def get_full_name(self):
        return self.full_name or self.username

    def get_short_name(self):
        return self.username

# Call this function during application initialization or in a management command.
create_default_subscription_plans()










# from mongoengine import Document, StringField, DecimalField, BooleanField, DateTimeField, IntField
# from datetime import timedelta

# class SubscriptionPlan(Document):
#     PLAN_TYPES = [("Monthly", "Monthly"), ("Yearly", "Yearly")]

#     name = StringField(max_length=100, unique=True)  # e.g., "Basic Monthly"
#     stripe_price_id = StringField(max_length=255, null=True)  # Required for Stripe
#     price = DecimalField(max_digits=10, decimal_places=2)
#     duration = StringField(choices=PLAN_TYPES)  # Monthly or Yearly
#     description = StringField(max_length=255, null=True)

#     def __str__(self):
#         return f"{self.name} - {self.duration} - ${self.price}"

#     @property
#     def duration_days(self):
#         """Convert plan duration into days for subscription calculations."""
#         return 30 if self.duration == "Monthly" else 365


# from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField, ImageField, ReferenceField
# from datetime import datetime, timedelta
# from mongoengine.fields import DateTimeField
# from bson import ObjectId
# from mongoengine import signals
# import pytz
# from django.contrib.auth.models import BaseUserManager
# from mongoengine import Document
# from mongoengine.fields import StringField

# # class CustomUserManager(BaseUserManager):
# #     def create_user(self, username, email, password=None, **extra_fields):
# #         if not email:
# #             raise ValueError("The Email field must be set")
# #         email = self.normalize_email(email)
# #         user = self.model(username=username, email=email, **extra_fields)
# #         user.set_password(password)
# #         user.save()
# #         return user

# #     def create_superuser(self, username, email, password=None, **extra_fields):
# #         extra_fields.setdefault('is_staff', True)
# #         extra_fields.setdefault('is_superuser', True)

# #         return self.create_user(username, email, password, **extra_fields)
    
# from mongoengine import Document
# from mongoengine.fields import StringField, EmailField, BooleanField, DateTimeField, ImageField, DecimalField, ReferenceField
# from datetime import datetime
# from datetime import datetime
# from bson import ObjectId
# from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField, ImageField, DecimalField, ReferenceField
# from .models import SubscriptionPlan  # Import SubscriptionPlan model
# from django.contrib.auth.hashers import make_password  # For hashing passwords

# class CustomUser(Document):
#     id = StringField(primary_key=True, default=lambda: str(ObjectId()))  # Generate unique user ID
#     username = StringField(max_length=150, unique=True)
#     email = EmailField(unique=True)
#     password = StringField(max_length=128)

#     full_name = StringField(max_length=255, null=True)
#     dob = DateTimeField(null=True)  # DateTimeField, but consider using DateField if you don't need time
#     gender = StringField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True)
#     bio = StringField(null=True)
#     profile_image = ImageField(null=True)  # Assuming it's a reference to an image

#     is_active = BooleanField(default=True)
#     is_staff = BooleanField(default=False)
#     is_superuser = BooleanField(default=False)

#     # Subscription Fields (Merged from UserSubscription)
#     plan = ReferenceField(SubscriptionPlan, null=True)  # Link to SubscriptionPlan
#     price = DecimalField(max_digits=10, decimal_places=2, null=True)
#     is_active_subscription = BooleanField(default=False)
#     start_date = DateTimeField(null=True)
#     end_date = DateTimeField(null=True)

#     stripe_price_id = StringField(max_length=255, null=True)
#     stripe_subscription_id = StringField(max_length=255, unique=True, null=True)

#     created_at = DateTimeField(default=datetime.now)  # Account creation timestamp

#     # Override the save method to hash password before saving
#     def save(self, *args, **kwargs):
#         if self.password:
#             self.password = make_password(self.password)  # Hash password before saving
#         super(CustomUser, self).save(*args, **kwargs)

#     def __str__(self):
#         return self.username
