from django.urls import path
from .views import login_view, logout_view, register
from . import views   # Import the views module

app_name = 'user_profile'  # This is the namespace for the URLs in this app

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/',views.register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),

]
