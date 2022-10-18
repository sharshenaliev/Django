from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('register', register, name='register'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('search', search, name='search'),
    path('org/<int:organization_id>/', get_org, name='org'),
    path('scan', scan, name='scan'),

]