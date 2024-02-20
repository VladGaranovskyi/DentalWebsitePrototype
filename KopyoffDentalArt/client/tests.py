from django.test import TestCase
from .models import Comment
from datetime import date

class CommentModelTestCase(TestCase):
    def setUp(self):
        # Create some sample comments
        self.comment1 = Comment.objects.create(
            name='John Doe',
            content='Test comment 1',
        )
        self.comment2 = Comment.objects.create(
            name='Jane Doe',
            content='Test comment 2',
        )

    def test_posted_on_auto_now(self):
        # Ensure that posted_on is automatically set to the current date
        self.assertEqual(self.comment1.posted_on, date.today())
        self.assertEqual(self.comment2.posted_on, date.today())

    def test_name_max_length(self):
        # Ensure that name field enforces max length
        max_length = self.comment1._meta.get_field('name').max_length
        self.assertEqual(max_length, 40)

    def test_content_max_length(self):
        # Ensure that content field enforces max length
        max_length = self.comment1._meta.get_field('content').max_length
        self.assertEqual(max_length, 400)
