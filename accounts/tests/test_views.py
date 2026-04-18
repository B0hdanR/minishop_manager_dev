from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import SupportRequest
from shop.models import Order

MY_ORDERS_URL = reverse("accounts:myorder-list")
SUPPORT_URL = reverse("accounts:support")


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


class UserTest(PrivateTestBase):
    def test_register_get(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_post(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "TestUser1",
                "email": "testenail1@gmail.com",
                "first_name": "TestFirst1",
                "last_name": "TestLast1",
                "password1": "GoodTest3751",
                "password2": "GoodTest3751",
            }
        )
        self.assertRedirects(response, reverse("accounts:login"))

    def test_user_list_forbidden_for_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:user-list"))
        self.assertEqual(response.status_code, 403)

    def test_user_update_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accounts:account-update"),
            {"first_name": "TestFirstNew", "last_name": "TestLastNew"},
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "TestFirstNew" )
        self.assertEqual(self.user.last_name, "TestLastNew")


class PublicMyOrdersTest(TestCase):
    def test_login_required(self):
        response = self.client.get(MY_ORDERS_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateMyOrdersTest(PrivateTestBase):
    def test_retrieve_my_orders(self):
        Order.objects.create(
            user=self.user,
            status="new",
        )
        Order.objects.create(
            user=self.user,
            status="completed",
        )
        response = self.client.get(MY_ORDERS_URL)
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.filter(user=self.user).order_by("-created_at")
        self.assertEqual(
            list(response.context["myorder_list"]),
            list(orders),
        )
        self.assertTemplateUsed(response, "accounts/myorder_list.html")

    def test_filter_myorder_by_status(self):
        Order.objects.create(
            user=self.user,
            status="new",
        )
        Order.objects.create(
            user=self.user,
            status="completed",
        )
        response = self.client.get(
            MY_ORDERS_URL,
            {"status": "new"}
        )
        orders = response.context["myorder_list"]
        self.assertEqual(orders.count(), 1)
        self.assertEqual(orders.first().status, "new")

    def test_user_sees_only_his_own_orders(self):
        not_user = get_user_model().objects.create_user(
            username="NotUser",
            password="notuser3863",
        )
        Order.objects.create(
            user=not_user,
            status="new",
        )
        Order.objects.create(
            user=self.user,
            status="completed",
        )
        response = self.client.get(MY_ORDERS_URL)
        orders = response.context["myorder_list"]
        self.assertEqual(orders.count(), 1)
        self.assertEqual(orders.first().user, self.user)


class SupportCreateTest(PrivateTestBase):
    def test_create_support_content_not_user(self):
        self.client.logout()
        response = self.client.post(
            SUPPORT_URL,
            {
                "title": "Support",
                "content": "Help",
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("shop:index"))
        self.assertTrue(
            SupportRequest.objects.filter(
                user__isnull=True,
                title="Support",
                content="Help",
            ).exists()
        )

    def test_create_support_content_user(self):
        response = self.client.post(
            SUPPORT_URL,
            {
                "title": "Support1",
                "content": "Help1",
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("shop:index"))
        self.assertTrue(
            SupportRequest.objects.filter(
                user=self.user,
                title="Support1",
                content="Help1",
            ).exists()
        )
