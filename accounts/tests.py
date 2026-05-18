from django.test import TestCase

from .forms import CustomUserCreationForm


class CustomUserCreationFormTest(TestCase):
    def form_data(self, telefono):
        return {
            'username': 'buyer',
            'email': 'buyer@example.com',
            'telefono': telefono,
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }

    def test_accepts_numeric_phone(self):
        form = CustomUserCreationForm(data=self.form_data('3001234567'))

        self.assertTrue(form.is_valid())

    def test_accepts_empty_phone(self):
        form = CustomUserCreationForm(data=self.form_data(''))

        self.assertTrue(form.is_valid())

    def test_rejects_phone_with_letters(self):
        form = CustomUserCreationForm(data=self.form_data('abc123'))

        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)
