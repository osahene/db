import requests as r
from accounts.models import User, Company
from django.contrib.auth import authenticate
from PAQSBackend.settings import GOOGLE_CLIENT_ID, SOCIAL_AUTH_PASSWORD
from rest_framework.exceptions import AuthenticationFailed



class Google:
    @staticmethod
    def validate(access_token):
        t = f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={access_token}"
        response = r.get(t)

        if response.status_code != 200:
            raise AuthenticationFailed("The token is either invalid or has expired")

        token_info = response.json()
        if token_info.get('aud') != GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("Invalid audience")
        
        if not token_info.get('email_verified', False):
            raise AuthenticationFailed("Email not verified by Google")

        return token_info
    
    @staticmethod
    def get_user_info(access_token):
        # Get user profile information using the People API
        people_api_url = "https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = r.get(people_api_url, headers=headers)

        if response.status_code != 200:
            raise AuthenticationFailed("Failed to fetch user info from Google People API")

        user_info = response.json()
        names = user_info.get('names', [{}])
        email_addresses = user_info.get('emailAddresses', [{}])

        if not names or not email_addresses:
            raise AuthenticationFailed("Failed to retrieve necessary user info")

        first_name = names[0].get('givenName', '')
        last_name = names[0].get('familyName', '')
        email = email_addresses[0].get('value', '')

        return first_name, last_name, email


def register_social_user(provider, email, first_name, last_name):
    # if user_type not in ['user', 'company']:
    #     raise ValueError("user_type must be 'user' or 'company'")

    # if user_type == 'user':
    #     user_model = User
    # else:
    #     user_model = Company
    user_model = User

    try:
        existing_user = user_model.objects.get(email=email)
        if provider == existing_user.auth_provider:
            authenticated_user = authenticate(email=email, password=SOCIAL_AUTH_PASSWORD)
            if authenticated_user:
                return {
                    'email': authenticated_user.email,
                    'first_name': authenticated_user.first_name,
                    'last_name': authenticated_user.last_name,
                    'tokens': authenticated_user.tokens()
                }
            else:
                raise AuthenticationFailed('Authentication failed. Please try again.')
        else:
            raise AuthenticationFailed(
                detail=f"Please continue your login with {existing_user.auth_provider}"
            )
    except user_model.DoesNotExist:
        new_user = user_model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            auth_provider=provider,
            is_verified=True
        )
        new_user.set_password(SOCIAL_AUTH_PASSWORD)
        new_user.save()

        authenticated_user = authenticate(email=email, password=SOCIAL_AUTH_PASSWORD)
        tokens = authenticated_user.tokens()
        return {
            'email': authenticated_user.email,
            'first_name': authenticated_user.first_name,
            'last_name': authenticated_user.last_name,
            "access_token": str(tokens.get('access')),
            "refresh_token": str(tokens.get('refresh'))
        }