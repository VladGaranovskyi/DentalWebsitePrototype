from django.db import models 
from datetime import datetime, time, timedelta
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

        today_appointments = self.filter(start_date__date=day_to_check)
        times = []
        times_dummy = []
        while start_datetime.timestamp() <= end_datetime.timestamp():
            times.append(start_datetime)
            start_datetime += timedelta(hours=1)
            
        for a in today_appointments:
            for t in times:
                if t.time() >= a.start_date.time() and t.time() < a.end_date.time():
                    print(t)
                    if t not in times_dummy:
                        times_dummy.append(t)
        
        return times == sorted(times_dummy)

    def block_range(self, day, times):
        dates = [datetime.strptime(day + " " + time, "%m/%d/%Y %I:%M %p") for time in times]
        date_dummy = None
        inc = 0
        for i, d in enumerate(dates):
            if d + timedelta(hours=1) in dates:
                if not date_dummy:
                    date_dummy = d
                inc += 1
            elif date_dummy:
                block = self.model(name="block", email="block@", message="block", service="block", insurance="block",
                start_date=date_dummy, end_date=date_dummy + timedelta(hours=inc+1))
                block.save()
                date_dummy = None
                inc = 0
            else:
                block = self.model(name="block", email="block@", message="block", service="block", insurance="block",
                start_date=d, end_date=d + timedelta(hours=1))
                block.save()
    
    def get_blocks(self):
        return self.filter(name="block")
    
    def get_blocked_days(self):
        appointments = self.all()
        if len(appointments) > 0:
            dates = []
            for a in appointments:
                if a.start_date.date() not in dates:
                    dates.append(a.start_date.date())
                elif a.end_date.date() not in dates:
                    dates.append(a.end_date.date())
            return [d.strftime("%m/%d/%Y") for d in dates if self.is_day_fully_booked(d)]        
        else:
            return []
            
