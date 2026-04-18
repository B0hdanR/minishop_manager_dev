from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.forms import SupportRequestForm, UserUpdateForm


class PrivateTestBase(TestCase):
    def setUp(self):
        username = "TestUser"
        password = "usertest456"
        email = "testemail@gmail.com"
        first_name = "test_first"
        last_name = "test_last"

        self.user = get_user_model().objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        self.client.force_login(self.user)


class FormsTests(PrivateTestBase):
    def test_support_form_is_valid(self):
        form = SupportRequestForm(
            data={"title": "Test Support", "content": "Help"}
        )
        self.assertTrue(form.is_valid())

    def test_user_update_form(self):
        form = UserUpdateForm(
            instance=self.user,
            data={
                "first_name": "Test_New",
                "last_name": "Test_New",
                "email": "testemail@gmail.com",
            }
        )
        self.assertTrue(form.is_valid())
