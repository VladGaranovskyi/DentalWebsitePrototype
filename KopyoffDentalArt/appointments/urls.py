from django.urls import path
from .views import BookingView, get_appointment, DashboardView, EditAppointmentView, BlockingView, ExpiredView, delete_absent_appointment, delete_present_appointment

urlpatterns = [
    path('booking/', BookingView.as_view(), name="booking"),
    path('info/', get_appointment, name="info"),
    path('dashboard/', DashboardView.as_view(), name="dashboard"),
    path('edit/', EditAppointmentView.as_view(), name="edit"),
    path('blocking/', BlockingView.as_view(), name="blocking"),
    path('expired/', ExpiredView.as_view(), name="expired"),
    path('delete_absent/<int:pk>', delete_absent_appointment, name="delete_absent"),
    path('delete_present/<int:pk>', delete_present_appointment, name="delete_present"),
]
