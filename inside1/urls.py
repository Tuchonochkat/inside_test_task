from django.contrib import admin
from django.urls import path

from authentication.views import LoginAPIView, MessageAPIView, DeleteAPIView, RegistrationAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/registration/', RegistrationAPIView.as_view()),
    path('api/login/', LoginAPIView.as_view()),
    path('api/message/', MessageAPIView.as_view()),
    path('api/delete_all_messages/', DeleteAPIView.as_view()),
]
