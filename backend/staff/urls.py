from django.urls import path
from . import views

urlpatterns = [
    path('auth/users/', views.FilteredUserView.as_view(), name='filtered-users'),
]