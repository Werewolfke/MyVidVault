from django.urls import path
from .views import RegisterView, LoginView, get_csrf_token, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('csrf/', get_csrf_token, name='get-csrf-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
]