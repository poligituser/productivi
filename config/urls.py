from django.urls import path
from django.views.generic import TemplateView

from accounts.views import RegisterView

urlpatterns = [
    path("", RegisterView.as_view(), name="register"),
    path("registered/", TemplateView.as_view(template_name="accounts/registered.html"), name="registered"),
]
