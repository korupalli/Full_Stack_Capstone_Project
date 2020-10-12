from django.conf.urls import url
from user.views import UserRegistrationView
from user.views import UserLoginView, Homepage

urlpatterns = [
    url(r'^signup', UserRegistrationView, name='signup'),
    url(r'^signin', UserLoginView, name='signin'),
    url(r'^homepage', Homepage.as_view(), name='logged_in'),
    ]