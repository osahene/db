from django.urls import path
from .views import GoogleOauthSignInview


urlpatterns=[
    path('google/', GoogleOauthSignInview.as_view(), name='google'),
    # path('github/', GithubOauthSignInView.as_view(), name='github')
]