from django.db import models
from datetime import datetime, time
import json


class AppointmentManager(models.Manager):

    def is_day_fully_booked(self, day_to_check):
        # Calculate the start and end datetime based on the day of the week
        if day_to_check.weekday() == 1 or day_to_check.weekday() == 3:  # Tuesday or Thursday
            start_time = time(9, 0)  # 9:00 AM
            end_time = time(19, 0)   # 7:00 PM
        elif day_to_check.weekday() == 5:  # Saturday
            start_time = time(9, 0)  # 9:00 AM
            end_time = time(16, 0)   # 4:00 PM
        else:
            return True

        # Combine the calculated time with the date
        start_datetime = datetime.combine(day_to_check, start_time)
        end_datetime = datetime.combine(day_to_check, end_time)

        # Query the database for overlapping appointments
        overlapping_appointments = self.filter(
            start_date__lte=end_datetime,
            end_date__gte=start_datetime
        )

        # If there are overlapping appointments, the day is not fully booked
        return not overlapping_appointments.exists()

    def block_range(self, start_date, end_date):
        appointment = self.model(name="block", email="block@", message="block", service="Dentures", insurance="1",
        start_date=datetime.strptime(start_date, "%m/%d/%Y %I:%M %p"), end_date=datetime.strptime(end_date, "%m/%d/%Y %I:%M %p"))
        appointment.save()
    
    def get_blocks(self):
        return self.filter(name="block")
    
    def get_blocked_days(self):
        appointments = self.all()
        if(len(appointments) > 0):
            dates = []
            for a in appointments:
                if a.start_date.date() not in dates:
                    dates.append(a.start_date.date())
                elif a.end_date.date() not in dates:
                    dates.append(a.end_date.date())
            return [d.strftime("%m/%d/%Y") for d in dates if self.is_day_fully_booked(d)]        
        else:
            return []
            
