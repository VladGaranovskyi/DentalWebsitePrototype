from django.db import models
from .managers import AppointmentManager

class Appointment(models.Model):  
    email = models.EmailField()
    name = models.CharField(max_length=40)
    message = models.TextField(max_length=400)
    service = models.CharField(max_length=30)
    insurance = models.CharField(max_length=30, default="1")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    objects = AppointmentManager()

    class Meta:
        ordering = ["-start_date"]
        indexes = [models.Index(fields=["start_date"], name="date_idx")]

    def get_date(self):
        return self.start_date.date().strftime("%m/%d/%Y")
    
    def get_time(self):
        return [self.start_date.time().strftime("%I:%M %p"), self.end_date.time().strftime("%I:%M %p")]
    
    def get_time_objects(self):
        return [self.start_date.time(), self.end_date.time()]
    
    def to_dict(self):
        time_range = self.get_time_objects()
        d = {
            "email": self.email,
            "name": self.name,
            "message": self.message,
            "service": self.service,
            "insurance": self.insurance,
            "start_time": time_range[0],
            "end_time": time_range[1],
            "date": self.start_date.date()
        }
        return d
    
    def to_json(self):
        time_range = self.get_time_objects()
        d = {
            "email": self.email,
            "name": self.name,
            "message": self.message,
            "service": self.service,
            "insurance": self.insurance,
            "start_time": time_range[0].strftime("%I:%M %p"),
            "end_time": time_range[1].strftime("%I:%M %p"),
        }
        return d


