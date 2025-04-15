import logging
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, logout
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status


# Set up a logger for internal errors
logger = logging.getLogger(__name__)

def get_user_from_token(request):
    """
    Utility function to decode JWT token and return the user.
    This function handles token expiration and invalid tokens.
    """
    token = request.COOKIES.get('jwt')
    
    if not token:
        logger.error('Authentication token not provided')
        return None  # Don't raise an exception, just return None
    
    try:
        # Decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = get_user_model().objects.get(id=payload['user_id'])
        return user
    except jwt.ExpiredSignatureError:
        return handle_session_expired(request)  # Token expired
    except jwt.InvalidTokenError:
        return handle_invalid_token()  # Invalid token
    except get_user_model().DoesNotExist:
        # raise AuthenticationFailed('User not found')
        logger.error('User not found') 
        return None




def handle_session_expired(request):
    """
    Handle session expiration: log out the user, delete the cookie, and return a message.
    """
    response = Response({'message': 'Session ended. Please log in again.'}, status=status.HTTP_401_UNAUTHORIZED)
    response.delete_cookie('jwt')
    logout(request)  # Log out the user on the backend
    return response




def handle_invalid_token():
    """
    Handle invalid token cases.
    """
    # raise AuthenticationFailed('Invalid token')
    logger.error('Invalid token') 
    return None
