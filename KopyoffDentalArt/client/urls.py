from django.urls import path
from .views import ContactView, HomeView, insurances_page_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('insurances/', insurances_page_view, name="insurances"),
    path('contact/', ContactView.as_view(), name="contact")
]
