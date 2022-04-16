from django.test import TestCase

from api.models import DeveloperModel


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        DeveloperModel.objects.create(
            email='testskf@gmail.com', name='SKF', organisation='OWASP', password="Skf@123")

    def test_email(self):
        developer = DeveloperModel.objects.get(email='testskf@gmail.com')
        field_label = developer._meta.get_field('email').verbose_name
        self.assertEqual(field_label, 'email')

    def test_organisation(self):
        developer = DeveloperModel.objects.get(email='testskf@gmail.com')
        field_label = developer._meta.get_field('organisation').verbose_name
        self.assertEqual(field_label, 'organisation')

    def test_password(self):
        developer = DeveloperModel.objects.get(email='testskf@gmail.com')
        field_label = developer._meta.get_field('password').verbose_name
        self.assertEqual(field_label, 'password')

    def test_(self):
        developer = DeveloperModel.objects.get(email='testskf@gmail.com')
        field_label = developer._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
