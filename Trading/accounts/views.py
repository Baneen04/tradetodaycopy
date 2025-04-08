# accounts/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, get_user_model
from accounts.serializer import UserSerializer, RegisterSerializer, SubscriptionPlanSerializer, SubscriptionPlan
from django.utils.timezone import now
from rest_framework.generics import RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

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
# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')

#         if not email or not password:
#             return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = CustomUser.objects.get(email=email)  # ✅ Get user by email
#         except CustomUser.DoesNotExist:
#             return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

#         # user = authenticate(request, username=user.username, password=password) 
#         user = authenticate(request, email=email, password=password) # ✅ Authenticate using username
#         if user is not None:
#                     # ✅ Update last_login manually
#             user.last_login = now()
#             user.save(update_fields=['last_login'])
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'user_id': user.id,
#                 'username': user.username,
#                 'email': user.email,
#                 'is_superuser': user.is_superuser,
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }, status=status.HTTP_200_OK)

#         return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
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
    authentication_classes = (JWTAuthentication,)
    queryset = CustomUser.objects.all().order_by("-is_staff")
    serializer_class = UserSerializer

## LOgin user details
class UserDetailAPIView(RetrieveAPIView):
    """API View for fetching logged-in user details."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UserSerializer

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user
    

# ✅ Delete a User (Only Admins Can Delete Users)
class UserDeleteAPIView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)  # ✅ Change to 200 OK
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# ### EDIT user profile
# class UserProfileUpdateAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = (JWTAuthentication,)

#     def put(self, request):
#         """
#         Update user profile by user ID or email (Authenticated Users Only).
#         """
#         user_id = request.data.get("user_id")
#         email = request.data.get("email")
#         full_name = request.data.get("full_name")
#         username = request.data.get("username")
#         dob = request.data.get("dob")
#         gender = request.data.get("gender")
#         bio = request.data.get("bio")
#         profile_image = request.FILES.get("profile_image")  # Handle image upload

#         # Ensure at least one identifier is provided
#         if not user_id and not email:
#             return Response({"error": "Provide either user_id or email to update profile."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             if user_id:
#                 user = CustomUser.objects.get(id=user_id)
#             elif email:
#                 user = CustomUser.objects.get(email=email)

#             # Ensure the authenticated user can only edit their own profile (except admins)
#             if request.user != user and not request.user.is_superuser:
#                 return Response({"error": "You do not have permission to update this profile."}, status=status.HTTP_403_FORBIDDEN)

#             # Update fields if provided
#             if full_name:
#                 user.full_name = full_name
#             if username:
#                 user.username = username
#             if dob:
#                 user.dob = dob
#             if gender:
#                 user.gender = gender
#             if bio:
#                 user.bio = bio
#             if profile_image:
#                 user.profile_image = profile_image  # Save the uploaded image

#             user.save()
#             return Response({"message": "Profile updated successfully", "user": UserSerializer(user).data}, status=status.HTTP_200_OK)

#         except CustomUser.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UserProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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
                user.email = email
            if full_name:
                user.full_name = full_name
            if username:
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
            return Response({
                "message": "Profile updated successfully",
                "user": UserSerializer(user).data
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
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # user = authenticate(request, username=user.username, password=password)
        user = authenticate(request, email=email, password=password)


        if user is None or not user.is_superuser:
            return Response({"error": "Invalid admin credentials"}, status=status.HTTP_403_FORBIDDEN)
                # ✅ Update last_login manually
        user.last_login = now()
        user.save(update_fields=['last_login'])
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Admin login successful",
            "admin_status": "Superuser",
            "user_id": user.id,
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
    authentication_classes = (JWTAuthentication,)
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
    authentication_classes = (JWTAuthentication,)

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


import stripe
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SubscriptionPlan
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import timedelta

# User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

# @csrf_exempt
# def create_checkout_session(request):
#     try:
#         data = json.loads(request.body)
#         plan_id = data.get("plan_id")
#         email = data.get("email")

#         if not email or not plan_id:
#             return JsonResponse({"error": "Email and Plan ID are required"}, status=400)

#         user, created = User.objects.get_or_create(email=email, defaults={"username": email})
#         plan = SubscriptionPlan.objects.get(id=plan_id)

#         session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             mode="subscription",
#             customer_email=email,
#             line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
#             success_url="http://127.0.0.1:8000/success/?session_id={CHECKOUT_SESSION_ID}",
#             # cancel_url="http://127.0.0.1:8000/cancel/",
#             metadata={"plan_id": plan.id, "user_id": user.id},
#         )

#         return JsonResponse({"sessionId": session.id})

#     except SubscriptionPlan.DoesNotExist:
#         return JsonResponse({"error": "Invalid plan selected"}, status=400)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)
    
# @csrf_exempt
# def payment_success(request):
#     session_id = request.GET.get("session_id")
#     if not session_id:
#         return JsonResponse({"error": "No session ID found"}, status=400)

#     try:
#         session = stripe.checkout.Session.retrieve(session_id)
#         email = session.get("customer_email")
#         plan_id = session["metadata"]["plan_id"]

#         plan = SubscriptionPlan.objects.get(id=plan_id)

#         stripe_customer_id = session.get("customer")
#         stripe_subscription_id = session.get("subscription")

#         user = User.objects.get(email=email)

#         # Activate subscription using the model method
#         user.activate_subscription(plan, plan.stripe_price_id, stripe_subscription_id)

#         return JsonResponse({
#             "message": "Subscription successful",
#             "user_id": user.id,
#             "plan": plan.name,
#             "price": str(plan.price),
#             "start_date": user.start_date.strftime("%Y-%m-%d %H:%M:%S"),
#             "end_date": user.end_date.strftime("%Y-%m-%d %H:%M:%S"),
#             "is_active_subscription": user.is_active_subscription
#         })

#     except SubscriptionPlan.DoesNotExist:
#         return JsonResponse({"error": "Invalid plan selected"}, status=400)
#     except User.DoesNotExist:
#         return JsonResponse({"error": "User not found"}, status=404)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)



# ✅ Get or Create Stripe Price ID
def get_or_create_stripe_price(plan):
    try:
        if plan.stripe_price_id:
            return plan.stripe_price_id  # Use existing price ID from DB

        # Check if a Stripe product with this exact name already exists
        existing_products = stripe.Product.list(limit=100).get("data", [])

        matched_product = next((p for p in existing_products if p["name"] == plan.name), None)

        if matched_product:
            # If product exists, check if a price is already available
            prices = stripe.Price.list(product=matched_product["id"], active=True).get("data", [])
            if prices:
                plan.stripe_price_id = prices[0]["id"]
                plan.save()
                return plan.stripe_price_id

            # If no price exists, create a new price for the existing product
            price = stripe.Price.create(
                unit_amount=int(plan.price * 100),  # Stripe uses cents
                currency="usd",
                recurring={"interval": "month" if plan.duration == "Monthly" else "year"},
                product=matched_product["id"],
            )
        else:
            # Create a new product and price if it doesn't exist
            product = stripe.Product.create(name=plan.name)
            price = stripe.Price.create(
                unit_amount=int(plan.price * 100),
                currency="usd",
                recurring={"interval": "month" if plan.duration == "Monthly" else "year"},
                product=product.id,
            )

        # Save and return price ID
        plan.stripe_price_id = price.id
        plan.save()
        return price.id

    except Exception as e:
        print("Stripe error:", str(e))
        return None 

# ✅ Create Stripe Checkout Session
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    data = json.loads(request.body)
    plan_id = data.get("plan_id")
    
    plan = SubscriptionPlan.objects.get(id=plan_id)
    stripe_price_id = get_or_create_stripe_price(plan)
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        customer_email=request.user.email,
        line_items=[{"price": stripe_price_id, "quantity": 1}],
        success_url="http://127.0.0.1:8000/user/payment-success/?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://127.0.0.1:8000/user/payment-cancel/",
        metadata={"plan_id": str(plan.id), "user_id": str(request.user.id)}
    )
   
    print(session)
    return Response({"session_id": session.id})
from django.shortcuts import redirect
# @api_view(["POST"])
# def create_checkout_session(request):
#     data = json.loads(request.body)
#     plan_id = data.get("plan_id")
    
#     try:
#         plan = SubscriptionPlan.objects.get(id=plan_id)
#         stripe_price_id = get_or_create_stripe_price(plan)
        
#         session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             mode="subscription",
#             customer_email=request.user.email,
#             line_items=[{"price": stripe_price_id, "quantity": 1}],
#             success_url="http://127.0.0.1:8000/user/payment-success/?session_id={CHECKOUT_SESSION_ID}",
#             cancel_url="http://127.0.0.1:8000/user/payment-cancel/",
#             metadata={"plan_id": str(plan.id), "user_id": str(request.user.id)}
#         )

#         print("Redirecting to:", session.url)  # Debugging purpose
#         return redirect(session.url)  # Redirect the user to Stripe Checkout

#     except SubscriptionPlan.DoesNotExist:
#         return Response({"error": "Invalid plan ID"}, status=400)
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)

# ✅ Handle Payment Success
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payment_success(request):
    session_id = request.GET.get("session_id")
    
    if not session_id:
        return Response({"error": "Session ID is required"}, status=400)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        user = request.user
        plan_id = session["metadata"].get("plan_id")
        
        if not plan_id:
            return Response({"error": "Plan ID missing from metadata"}, status=400)

        plan = SubscriptionPlan.objects.get(id=plan_id)
        stripe_subscription_id = session.get("subscription")

        if not stripe_subscription_id:
            return Response({"error": "Subscription ID missing from session"}, status=400)

        # ✅ Activate Subscription
        user.activate_subscription(plan, plan.stripe_price_id, stripe_subscription_id)
        
        return Response({"message": "Subscription successful"})
    
    except SubscriptionPlan.DoesNotExist:
        return Response({"error": "Plan not found"}, status=404)
    
    except Exception as e:
        return Response({"error": str(e)}, status=500)



# ✅ Cancel Subscription
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    user = request.user
    if not user.is_active_subscription:
        return Response({"error": "No active subscription found"}, status=400)
    
    stripe.Subscription.modify(user.stripe_subscription_id, cancel_at_period_end=True)
    user.deactivate_subscription()
    return Response({"message": "Subscription canceled"})

# ✅ Check Subscription Status
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def check_subscription_status(request):
#     user = request.user
#     if user.is_active_subscription:
#         return Response({
#             "active": True,
#              "plan": user.plan.name if user.plan else None,
#               "start_date": user.start_date,
#              "end_date": user.end_date})
#     return Response({"active": False})
from datetime import date
from datetime import date

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_subscription_status(request):
    user = request.user
    
    if user.is_active_subscription:
        today = date.today()
        end_date = user.end_date.date() if user.end_date else None  # Convert datetime to date
        days_left = (end_date - today).days if end_date else None

        return Response({
            "active": True,
            "plan": user.plan.name if user.plan else None,
            "start_date": user.start_date,
            "end_date": user.end_date,
            "days_left": max(days_left, 0) if days_left is not None else 0  # Ensure non-negative
        })

    return Response({"active": False, "days_left": 0})


# ✅ Stripe Webhook
# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.headers.get("Stripe-Signature")
#     event = None
#     try:
#         event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
#     except stripe.error.SignatureVerificationError:
#         return JsonResponse({"error": "Invalid signature"}, status=400)
    
#     if event["type"] == "invoice.payment_succeeded":
#         subscription_id = event["data"]["object"]["subscription"]
#         user = User.objects.filter(stripe_subscription_id=subscription_id).first()
#         if user:
#             user.activate_subscription(user.plan, user.plan.stripe_price_id, subscription_id)
    
#     return JsonResponse({"status": "success"})



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # ✅ Extract metadata
        subscription_id = session.get("subscription")
        user_id = session["metadata"].get("user_id")
        plan_id = session["metadata"].get("plan_id")

        if not subscription_id:
            return JsonResponse({"error": "Subscription ID missing from session"}, status=400)

        try:
            user = CustomUser.objects.get(id=user_id)
            plan = SubscriptionPlan.objects.get(id=plan_id)

            # ✅ Activate the subscription in your database
            user.activate_subscription(plan, plan.stripe_price_id, subscription_id)

            return JsonResponse({"message": "Subscription activated successfully!"})
        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except SubscriptionPlan.DoesNotExist:
            return JsonResponse({"error": "Subscription Plan not found"}, status=404)

    return JsonResponse({"error": "Unhandled event type"}, status=400)