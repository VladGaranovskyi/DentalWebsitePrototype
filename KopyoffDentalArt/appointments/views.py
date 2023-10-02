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
from django.utils import timezone


def get_all_dates():
    appointments = Appointment.objects.all().exclude(name="block")
    if len(appointments) > 0:
        dates = {}
        for a in appointments:
            try:
                dates[a.get_date()].append(a.get_time())
            except KeyError:
                dates[a.get_date()] = [a.get_time()]
        return json.dumps(dates)
    else:
        return json.dumps(dict())

insurance_list = [
    "Delta Dental: Individual Preferred Plan",
    "Delta Dental: Network Premier",
    "Delta Dental: Patient Direct",
    "Delta Dental: PPO",
    "Delta Dental: PPO Family High Plan",
    "Delta Dental: PPO Family Low Plan",
    "Delta Dental: PPO Plus Premier",
    "Delta Dental: PPO Plus Premier Individual Choice",
    "Delta Dental: PPO Preferred Plan for Families",
    "Delta Dental: Federal Employees Dental Program",
    "Delta Dental: PPO Plan A",
    "Delta Dental: PPO Plan B",
    "Delta Dental: Simple Access",
    "Delta Dental: TRICARE Retiree Dental Program",
    "Aetna: Dental PPO 50 (High Option)",
    "Aetna: Individual Advantage(SM) Dental PPO",
    "Aetna: Assurant Dental Health Alliance (PPO)",
    "Aetna: HealthFund/ DentalFund with PPO II Network",
    "Aetna: HealthFund®/ DentalFund®",
    "Aetna: Dental EPP with PPO II Network",
    "Aetna: Dental PPO/PDN",
    "Aetna: Dental PPO/PDN with PPO II Network",
    "Aetna: Costco Core PPO",
    "AIG: PPO",
    "Ameritas: Classic(PPO)",
    "Assurant Employee Benefits: Assurant Dental Network PPO",
    "Careington: Care Platinum Series PPO Plan",
    "Careington: Care Platinum POS Plan",
    "Cigna: Dental PPO",
    "Cigna: Dental PPO: Radius Network",
    "Cigna: Dental PPO: Advantage Dentists",
    "Cigna: Dental PPO (Core Network)",
    "Cigna: Dental EPO: Radius Network",
    "Connection Dental: PPO",
    "Connection Dental: GEHA Federal",
    "Dental Benefit Providers: Healthplex PPO Network",
    "Dental Health Alliance: Sun Life Financial (Network)",
    "Dental Health Alliance: DHA Assurant (Network)",
    "Dental Health Alliance: DHA Premier",
    "Dental Source: DenteMax",
    "Dentegra: Family Preferred Plan",
    "EmblemHealth: Preferred Plus Dental",
    "GEHA: CONNECTION Dental Plus",
    "Guardian: Dental PPO",
    "Guardian: PPO: DentalGuard Preferred",
    "Guardian: PPO: DentalGuard Preferred/Premier",
    "GWH-Cigna (formerly Great West Healthcare): PPO",
    "Healthplex: PPO Panels: Careington PPO Panel",
    "Horizon Blue Cross Blue Shield of New Jersey: Horizon Dental PPO",
    "MetLife: PDP",
    "MetLife: PDP Plus (Preferred Dentist Program)",
    "Moda Health: Delta Dental PPO",
    "Moda Health: Delta Dental Premier",
    "PBA (Patrolmens Benefit Association): Dental Plan",
    "Principal Financial Group: Principal Plan PPO",
    "Renaissance Dental: Dentamax PPO",
    "Solstice: PPO",
    "Solstice: PPO (ASO Network)",
    "Sun Life Financial: Active Plan (PPO)",
    "Sun Life Financial: DenteMax",
    "Sun Life Financial: Premier Dental",
    "Union Plans: Patrolmens Benevolent Association",
    "Union Plans: Patrolmens Benevolent Association PPO",
    "Union Plans: 1199 SEIU",
    "United Concordia: Tricare Active Duty Dental Program (ADDP)",
    "UnitedHealthcare: Dental PPO"
]


class BookingView(View):   

    def get(self, request):
        blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
        return render(request, "booking.html", {"dates": get_all_dates(), "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days())
                                                , "insurance_list": json.dumps(insurance_list)})
    
    def post(self, request):
        if "appointment_id" in request.COOKIES.keys() and not request.user.is_authenticated:
            return redirect(reverse("info"))
        errors = []
        service = request.POST["service"]
        insurance = request.POST["insurance"]
        if insurance not in insurance_list:
            errors.append("This insurance is not allowed")  
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
                if (a.start_date.time() <= start_date.time() and a.end_date.time() > start_date.time())\
                or (a.start_date.time() <= end_date.time() and a.end_date.time() > end_date.time()):
                    errors.append("this time has already been taken")
                    break
        if not validate_email(email, check_mx=True):
            errors.append("email is invalid")
        if errors:
            blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
            return render(request, "booking.html", {"dates": get_all_dates(), "errors": errors, 
                            "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days()), "insurance_list": json.dumps(insurance_list)})
        else:
            appointment = Appointment(service=service, insurance=insurance, name=name, email=email, message=message, start_date=start_date, end_date=end_date)
            appointment.save()
            send_mail(
                "Dr. Helen Kopyoff",
                f"Congratulations! You have successfully booked appointment on {appointment.get_date()} from {appointment.get_time()[0]} to {appointment.get_time()[1]}",
                "info@kopyoffdentalart.com",
                [email],
                fail_silently=True,
            )
            response = redirect(reverse("info"))
            response.set_cookie(key="appointment_id", value=appointment.id, secure=True, expires=datetime.strftime(appointment.end_date, "%a, %d-%b-%Y %H:%M:%S GMT"))
            return response


class EditAppointmentView(View): 

    def get(self, request):
        appointment = Appointment.objects.get(pk=request.COOKIES["appointment_id"])
        blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
        return render(request, "edit_appointment.html", {"dates": get_all_dates(), "appointment": appointment, 
        "date": appointment.get_date(), "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days()), 
        "insurance_list": json.dumps(insurance_list)})
    
    def post(self, request):
        appointment = Appointment.objects.get(pk=request.COOKIES["appointment_id"])
        errors = []
        service = request.POST["service"]
        insurance = request.POST["insurance"]
        if insurance not in insurance_list:
            errors.append("This insurance is not allowed")  
        name = request.POST["name"]
        if len(name) > 40:
            errors.append("name is too big, must be less than 40 characters")
        email = request.POST["email"]
        message = request.POST["message"]        
        if len(message) > 400:
            errors.append("message is too big, must be less than 400 characters")
        # start_date = datetime.strptime(request.POST["date"] + " " + request.POST["time"], "%m/%d/%Y %I:%M %p")
        # end_date = start_date + timedelta(hours=1)
        # appointments = Appointment.objects.filter(start_date__date=start_date.date())
        # if len(appointments) > 0:
        #     for a in appointments:
        #         if (a.start_date.timestamp() <= start_date.timestamp() and a.end_date.timestamp() > start_date.timestamp())\
        #         or (a.start_date.timestamp() <= end_date.timestamp() and a.end_date.timestamp() > end_date.timestamp()):
        #             errors.append("this time has already been taken")
        #             break
        if not validate_email(email, check_mx=True):
            errors.append("email is invalid")
        if errors:
            blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
            return render(request, "edit_appointment.html", {"dates": get_all_dates(), "errors": errors, "appointment": appointment,
            "date": appointment.get_date(), "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days())
            , "insurance_list": json.dumps(insurance_list)})
        else:
            appointment.name = name
            appointment.email = email
            appointment.message = message
            appointment.service = service
            appointment.insurance = insurance
            # appointment.start_date = start_date
            # appointment.end_date = end_date
            appointment.save()
            response = redirect(reverse("info"))
            response.set_cookie(key="appointment_id", value=appointment.id, secure=True, expires=datetime.strftime(appointment.end_date, "%a, %d-%b-%Y %H:%M:%S GMT"))
            return response
        

class BookingAdminView(View, LoginRequiredMixin):

    def get(self, request):
        blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
        return render(request, "booking_admin.html", {"dates": get_all_dates(), "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days())
                                                      , "insurance_list": json.dumps(insurance_list)})
    
    def post(self, request):
        errors = []
        service = request.POST["service"]
        insurance = request.POST["insurance"]
        if insurance not in insurance_list:
            errors.append("This insurance is not allowed")       
        start_date = datetime.strptime(request.POST["date"] + " " + request.POST["time"], "%m/%d/%Y %I:%M %p")
        end_date = start_date + timedelta(hours=1)
        appointments = Appointment.objects.filter(start_date__date=start_date.date())
        if len(appointments) > 0:
            for a in appointments:
                if (a.start_date.time() <= start_date.time() and a.end_date.time() > start_date.time())\
                or (a.start_date.time() <= end_date.time() and a.end_date.time() > end_date.time()):
                    errors.append("this time has already been taken")
                    break
        if errors:
            blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
            return render(request, "booking_admin.html", {"dates": get_all_dates(), "errors": errors, 
                                                    "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days())
                                                    , "insurance_list": json.dumps(insurance_list)})
        else:
            appointment = Appointment(service=service, insurance=insurance, name="Patient", email="Patient@", message="Hello", start_date=start_date, end_date=end_date)
            appointment.save()
            return redirect(reverse("dashboard"))



def get_appointment(request):
    appointment = get_object_or_404(Appointment, pk=request.COOKIES.get("appointment_id"))
    pay_or_not = timezone.make_aware(datetime.now(), timezone.get_default_timezone()) > appointment.start_date - timedelta(days=7)
    return render(request, "appointment.html", {"appointment": appointment, "pay_or_not": pay_or_not})


class DashboardView(TemplateView, LoginRequiredMixin):
    template_name = "appointments.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        appointments = [a.to_dict() for a in Appointment.objects.filter(start_date__date=datetime.now().date()).exclude(name="block")]
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
        all_appointments = Appointment.objects.all().exclude(name="block")
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
        blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
        return render(request, "blocking.html", {"dates": get_all_dates(), "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days())
                                                      , "insurance_list": json.dumps(insurance_list), "blocks_view": Appointment.objects.get_blocks()})
    
    def post(self, request):
        blockings = [[a.start_date.strftime("%m/%d/%Y %I:%M %p"), a.end_date.strftime("%m/%d/%Y %I:%M %p")] for a in Appointment.objects.get_blocks()]
        Appointment.objects.block_range(request.POST["day"], request.POST.getlist("times"))
        return render(request, "blocking.html", {"dates": get_all_dates(), "blocks": json.dumps(blockings), "blocked_days": json.dumps(Appointment.objects.get_blocked_days())
                                                      , "insurance_list": json.dumps(insurance_list), "blocks_view": Appointment.objects.get_blocks()})


class ExpiredView(TemplateView, LoginRequiredMixin):
    template_name = "expired_appointments.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["appointments"] = Appointment.objects.filter(end_date__lt=datetime.now()).exclude(name="block")

        return context


def cancel_appointment(request, pk):
    appointment = Appointment.objects.get(pk=pk)
    if timezone.make_aware(datetime.now(), timezone.get_default_timezone()) > appointment.start_date - timedelta(days=7):
        send_mail(
            "Dr. Helen Kopyoff Cancel",
            "Sorry, but you canceled the appointment before 7 days, you need to pay 50$",
            "info@kopyoffdentalart.com",
            [appointment.email],
            fail_silently=True,
        )
    appointment.delete()
    response = redirect(reverse("booking"))  
    response.delete_cookie("appointment_id")
    return response


@login_required
def delete_absent_appointment(request, pk):
    appointment = Appointment.objects.get(pk=pk)
    send_mail(
        "Dr. Helen Kopyoff Absense Fee",
        "Sorry, but you didn't show up at the appointment, you need to pay 50$",
        "info@kopyoffdentalart.com",
        [appointment.email],
        fail_silently=True,
    )
    appointment.delete()
    return redirect(reverse("expired"))    


@login_required
def delete_present_appointment(request, pk):
    Appointment.objects.get(pk=pk).delete()
    return redirect(reverse("expired"))   


@login_required
def delete_block(request, pk):
    Appointment.objects.get(pk=pk).delete()
    return redirect(reverse("blocking"))        
            

        
    

