from django.test import TestCase
from .models import Appointment
from datetime import datetime, timedelta

class AppointmentModelTestCase(TestCase):
    def setUp(self):
        # Create some sample appointments
        self.appointment1 = Appointment.objects.create(
            email='test1@example.com',
            name='John Doe',
            message='Test message 1',
            service='Service 1',
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(hours=1)
        )
        self.appointment2 = Appointment.objects.create(
            email='test2@example.com',
            name='Jane Doe',
            message='Test message 2',
            service='Service 2',
            start_date=datetime.now() + timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1, hours=1)
        )

    def test_get_date(self):
        self.assertEqual(self.appointment1.get_date(), datetime.now().strftime("%m/%d/%Y"))

    def test_get_time(self):
        self.assertEqual(self.appointment1.get_time(), [
            datetime.now().time().strftime("%I:%M %p"),
            (datetime.now() + timedelta(hours=1)).time().strftime("%I:%M %p")
        ])

    def test_get_time_objects(self):
        self.assertEqual(self.appointment1.get_time_objects(), [
            datetime.now().time(),
            (datetime.now() + timedelta(hours=1)).time()
        ])

    def test_to_dict(self):
        appointment_dict = self.appointment1.to_dict()
        self.assertEqual(appointment_dict['email'], 'test1@example.com')
        self.assertEqual(appointment_dict['name'], 'John Doe')
        # Continue with other assertions for the dictionary keys/values

    def test_to_json(self):
        appointment_json = self.appointment1.to_json()
        self.assertEqual(appointment_json['email'], 'test1@example.com')
        self.assertEqual(appointment_json['name'], 'John Doe')
        # Continue with other assertions for the JSON keys/values
