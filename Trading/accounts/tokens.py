from rest_framework_simplejwt.tokens import Token
from bson import ObjectId

class MongoToken(Token):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        # Ensure the user ID is stored as a string
        token[cls.payload['user_id']] = str(user.id)
        return token

class MongoAccessToken(MongoToken):
    token_type = 'access'
    lifetime = None  # Will use settings.ACCESS_TOKEN_LIFETIME

class MongoRefreshToken(MongoToken):
    token_type = 'refresh'
    lifetime = None  # Will use settings.REFRESH_TOKEN_LIFETIME 