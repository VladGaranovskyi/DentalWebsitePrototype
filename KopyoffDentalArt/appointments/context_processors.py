from .models import Appointment
from datetime import datetime

def header_processor(request):
    return {"count_of_expired_appointments": len(Appointment.objects.filter(end_date__lt=datetime.now()).exclude(name="block"))}