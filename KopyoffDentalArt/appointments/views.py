from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from validate_email import validate_email
from .models import Appointment
from datetime import datetime, timedelta
import json
from django.core.mail import send_mail


def get_all_dates():
    appointments = Appointment.objects.all()
    if len(appointments) > 0:
        dates = {}
        for a in appointments:
            if a.name != "block":
                try:
                    dates[a.get_date()].append(a.get_time())
                except KeyError:
                    dates[a.get_date()] = [a.get_time()]
        return json.dumps(dates)
    else:
        return json.dumps(dict())


class BookingView(View):   

    def get(self, request):
        blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
        return render(request, "booking.html", {"dates": get_all_dates(), "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days())})
    
    def post(self, request):
        if "appointment_id" in request.COOKIES.keys() and not request.user.is_authenticated:
            return redirect(reverse("info"))
        errors = []
        service = request.POST["service"]
        insurance = request.POST["insurance"]
        name = request.POST["name"]
        if len(name) > 40:
            errors.append("name is too big, must be less than 40 characters")
        email = request.POST["email"]
        message = request.POST["message"]        
        if len(message) > 400:
            errors.append("message is too big, must be less than 400 characters")
        start_date = datetime.strptime(request.POST["date"] + " " + request.POST["time"], "%m/%d/%Y %I:%M %p")
        end_date = start_date + timedelta(hours=1)
        appointments = Appointment.objects.filter(start_date__date=start_date.date())
        if len(appointments) > 0:
            for a in appointments:
                if (a.start_date <= start_date and a.end_date > start_date) or (a.start_date <= end_date and a.end_date > end_date):
                    errors.append("this time has already been taken")
                    break
        if not validate_email(email, verify=True):
            errors.append("email is invalid")
        if errors:
            blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
            return render(request, "booking.html", {"dates": get_all_dates(), "errors": errors, 
                                                    "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days())})
        else:
            appointment = Appointment(service=service, insurance=insurance, name=name, email=email, message=message, start_date=start_date, end_date=end_date)
            appointment.save()
            send_mail(
                "Dr. Helen Kopyoff",
                f"Congratulations! You have successfully booked appointment from {appointment.get_time()[0]} to {appointment.get_time()[1]}",
                "info@kopyoffdentalart.com",
                [email],
                fail_silently=False,
            )
            response = redirect(reverse("info"))
            response.set_cookie(key="appointment_id", value=appointment.id, secure=True, expires=datetime.strftime(appointment.end_date, "%a, %d-%b-%Y %H:%M:%S GMT"))
            return response


class EditAppointmentView(View): 

    def get(self, request):
        appointment = Appointment.objects.get(pk=request.COOKIES["appointment_id"])
        blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
        return render(request, "edit_appointment.html", {"dates": get_all_dates(), "appointment": appointment, 
        "date": appointment.get_date(), "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days())})
    
    def post(self, request):
        appointment = Appointment.objects.get(pk=request.COOKIES["appointment_id"])
        errors = []
        service = request.POST["service"]
        insurance = request.POST["insurance"]
        name = request.POST["name"]
        if len(name) > 40:
            errors.append("name is too big, must be less than 40 characters")
        email = request.POST["email"]
        message = request.POST["message"]        
        if len(message) > 400:
            errors.append("message is too big, must be less than 400 characters")
        start_date = datetime.strptime(request.POST["date"] + " " + request.POST["time"], "%m/%d/%Y %I:%M %p")
        end_date = start_date + timedelta(hours=1)
        appointments = Appointment.objects.filter(start_date__date=start_date.date())
        if len(appointments) > 0:
            for a in appointments:
                if (a.start_date.timestamp() <= start_date.timestamp() and a.end_date.timestamp() > start_date.timestamp())\
                or (a.start_date.timestamp() <= end_date.timestamp() and a.end_date.timestamp() > end_date.timestamp()):
                    errors.append("this time has already been taken")
                    break
        if validate_email(email, verify=True):
            errors.append("email is invalid")
        if errors:
            blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
            return render(request, "edit_appointment.html", {"dates": get_all_dates(), "errors": errors, "appointment": appointment,
            "date": appointment.get_date(), "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_datys())})
        else:
            appointment.name = name
            appointment.email = email
            appointment.message = message
            appointment.service = service
            appointment.insurance = insurance
            appointment.start_date = start_date
            appointment.end_date = end_date
            appointment.save()
            send_mail(
                "Dr. Helen Kopyoff",
                f"Congratulations! You have successfully edited your appointment from {appointment.get_time()[0]} to {appointment.get_time()[1]}",
                "info@kopyoffdentalart.com",
                [email],
                fail_silently=False,
            )
            response = redirect(reverse("info"))
            response.set_cookie(key="appointment_id", value=appointment.id, secure=True, expires=datetime.strftime(appointment.end_date, "%a, %d-%b-%Y %H:%M:%S GMT"))
            return response
        

def get_appointment(request):
    appointment = get_object_or_404(Appointment, pk=request.COOKIES.get("appointment_id"))
    return render(request, "appointment.html", {"appointment": appointment})


class DashboardView(TemplateView, LoginRequiredMixin):
    template_name = "appointments.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        appointments = [a.to_dict() for a in Appointment.objects.filter(start_date__date=datetime.now().date())]
        if appointments:
            for a in appointments:
                start_date = datetime.combine(a["date"], a["start_time"])
                end_date = datetime.combine(a["date"], a["end_time"])
                if start_date > datetime.now():
                    a["state"] = "upcoming"
                elif start_date < datetime.now() and datetime.now() < end_date:
                    a["state"] = "current"
                elif datetime.now() > end_date:
                    a["state"] = "empty"
        context["appointments"] = appointments
        all_appointments = Appointment.objects.all()
        dates = {}
        if len(all_appointments) > 0:
            for a in all_appointments:
                try:
                    dates[a.get_date()].append(a.to_json())
                except KeyError:
                    dates[a.get_date()] = [a.to_json()]
        context["all_appointments"] = json.dumps(dates)
        return context


class BlockingView(View, LoginRequiredMixin):

    def get(self, request):
        return render(request, "blocking.html", {"blocks": Appointment.objects.get_blocks()})
    
    def post(self, request):
        Appointment.objects.block_range(request.POST["date_from"], request.POST["date_to"])
        return render(request, "blocking.html", {"blocks": Appointment.objects.get_blocks()})


class ExpiredView(TemplateView, LoginRequiredMixin):
    template_name = "expired_appointments.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["appointments"] = Appointment.objects.filter(end_date__lt=datetime.now()).exclude(name="block")

        return context


@login_required
def delete_absent_appointment(request, pk):
    appointment = Appointment.objects.get(pk=pk)
    send_mail(
        "Dr. Helen Kopyoff Absense Fee",
        "Sorry, but you didn't show up at the appointment, you need to pay 50$. If you weren't absent and we are wrong, please, contact us, and tell us about this",
        "info@kopyoffdentalart.com",
        [appointment.email],
        fail_silently=False,
    )
    return redirect(reverse("expired"))    

@login_required
def cancel_appointment(request, pk):
    appointment = Appointment.objects.get(pk=pk)
    send_mail(
        "Dr. Helen Kopyoff Cancel",
        "Sorry, but you canceled the appointment, you need to pay 25$. If you didn't cancel your appointment, please, contact us, and tell us about this",
        "info@kopyoffdentalart.com",
        [appointment.email],
        fail_silently=False,
    )
    return redirect(reverse("expired"))  

@login_required
def delete_present_appointment(request, pk):
    Appointment.objects.get(pk=pk).delete()
    return redirect(reverse("expired"))   

@login_required
def delete_block(request, pk):
    Appointment.objects.get(pk=pk).delete()
    return redirect(reverse("blocking"))        
            

        
    

