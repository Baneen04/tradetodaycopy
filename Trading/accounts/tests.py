from datetime import timedelta
from django.utils.timezone import now
from accounts.models import CustomUser, SubscriptionPlan

# Create a Subscription Plan (if not exists)
plan, _ = SubscriptionPlan.objects.get_or_create(name="Monthly Plan", price=20.00, duration= "Monthly")

# Create User 1 with an active subscription
user1 = CustomUser.objects.create(
    username="active_user",
    email="active@example.com",
    is_active=True
)

user1.set_password("123")  # Set password securely
user1.plan = plan
user1.price = plan.price
user1.is_active_subscription = True
user1.start_date = now()
user1.end_date = now() + timedelta(days=plan.duration)
user1.stripe_price_id = "stripe_price_123"
user1.stripe_subscription_id = "stripe_sub_123"
user1.save()

# Create User 2 without a subscription
user2 = CustomUser.objects.create(
    username="inactive1_user",
    email="inactive1@example.com",
    is_active=True,
    is_active_subscription=False  # No active subscription
)

user2.set_password("123")
user2.save()

print("✅ Users created successfully.")
