# th_monitoring/urls.py

from django.urls import path
from . import views

app_name = 'th_monitoring'

urlpatterns = [ 
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Make sure name matches
    path('dashboard/trend_page/', views.trend_page, name='trend_page'),
    path('email-settings/', views.email_settings, name='email_settings'),
    path('email-alerts/', views.email_alerts, name='email_alerts'),

]
