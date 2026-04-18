from http.client import responses

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from shop.models import Product, ProductCategory, Order, OrderItem

PRODUCTCATEGORY_URL = reverse("shop:productcategory-list")
PRODUCT_URL = reverse("shop:product-list")


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


class PublicProductCategoryTest(TestCase):
    def test_login_required(self):
        response = self.client.get(PRODUCTCATEGORY_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateProductCategoryTest(PrivateTestBase):
    def test_retrieve_product_categories(self):
        ProductCategory.objects.create(
            name="Test_Product_Category_1",
        )
        ProductCategory.objects.create(
            name="Test_Product_Category_2",
        )
        response = self.client.get(PRODUCTCATEGORY_URL)
        self.assertEqual(response.status_code, 200)
        productcategories = ProductCategory.objects.all()
        self.assertEqual(
            list(response.context["productcategory_list"]),
            list(productcategories)
        )
        self.assertTemplateUsed(response, "shop/productcategory_list.html")

    def test_filter_categories_by_name(self):
        ProductCategory.objects.create(
            name="Test_Product_Category_1",
        )
        ProductCategory.objects.create(
            name="Test_Product_Category_2",
        )
        response = self.client.get(
            PRODUCTCATEGORY_URL,
            {"name": "Test_Product_Category_1"}
        )
        self.assertContains(response, "Test_Product_Category_1")
        self.assertNotContains(response, "Test_Product_Category_2")


class PublicProductTest(TestCase):
    def test_login_required(self):
        response = self.client.get(PRODUCT_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateProductTest(PrivateTestBase):
    def test_retrieve_products(self):
        productcategory = ProductCategory.objects.create(name="Test_Product_Category")
        Product.objects.create(
            name="Test_Product_1",
            category=productcategory,
            price=200
        )
        Product.objects.create(
            name="Test_Product_2",
            category=productcategory,
            price=220
        )

        response = self.client.get(PRODUCT_URL)
        self.assertEqual(response.status_code, 200)
        products = Product.objects.all()
        self.assertEqual(
            list(response.context["product_list"]),
            list(products)
        )
        self.assertTemplateUsed(response, "shop/product_list.html")

    def test_filter_products_by_name(self):
        productcategory = ProductCategory.objects.create(name="Test_Product_Category")
        Product.objects.create(
            name="Test_Product_1",
            category=productcategory,
            price=200
        )
        Product.objects.create(
            name="Test_Product_2",
            category=productcategory,
            price=220
        )

        response = self.client.get(PRODUCT_URL, {"name": "Test_Product_1"})
        self.assertContains(response, "Test_Product_1")
        self.assertNotContains(response, "Test_Product_2")


class OrderTestBase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username="staff_user",
            password="staff3567445",
            is_staff=True,
        )
        self.employee_user = User.objects.create_user(
            username="employee_user",
            password="employee3567445",
            is_employee=True,
        )
        self.regular_user = User.objects.create_user(
            username="regular_user",
            password="regular367337845",
        )
        self.category = ProductCategory.objects.create(name="Test_Product_Category")
        self.product = Product.objects.create(
            name="Test_Product_1",
            category=self.category,
            stock_quantity=20,
            price=220
        )
        self.order = Order.objects.create(
            user=self.regular_user,
            status="new"
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=10,
        )
        self.order_list_url = reverse("shop:order-list")
        self.order_detail_url = reverse(
            "shop:order-detail",
            args=[self.order.pk]
        )


class OrderListTest(OrderTestBase):
    def test_order_list_forbidden_for_regular_user(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, 403)

    def test_order_list_allowed_for_employee_users(self):
        self.client.force_login(self.employee_user)
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, 200)

    def test_order_list_allowed_for_staff_users(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, 200)


class OrderDetailTest(OrderTestBase):
    def test_order_detail_forbidden_for_regular_user(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, 403)

    def test_order_detail_allowed_for_employee_users(self):
        self.client.force_login(self.employee_user)
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, 200)

    def test_order_detail_allowed_for_staff_users(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, 200)

    def test_staff_can_update_order_status(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(
            self.order_detail_url,
            {"status": "processing"}
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "processing")
        self.assertRedirects(response, self.order_detail_url)

    def test_regular_user_cannot_update_order(self):
        self.client.force_login(self.regular_user)
        response = self.client.post(
            self.order_detail_url,
            {"status": "processing"}
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "new")
        self.assertEqual(response.status_code, 403)


class CartTestBase(TestCase):
    def setUp(self):
        username = "TestUser7"
        password = "usertest4567"
        email = "testemail7@gmail.com"
        first_name = "test_first7"
        last_name = "test_last7"

        self.user = get_user_model().objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        self.client.force_login(self.user)

        self.productcategory = ProductCategory.objects.create(name="Test_Product_Category")
        self.product = Product.objects.create(
            name="Test_Product_1",
            category=self.productcategory,
            stock_quantity=20,
            price=200,
        )


class AddToCartTest(CartTestBase):
    def test_add_to_cart_creates_order(self):
        self.client.post(
            reverse("shop:add-to-cart", args=[self.product.pk]),
            {"quantity": 1}
        )
        order = Order.objects.get(user=self.user, status="new")
        item = order.items.get(product=self.product)
        self.assertEqual(item.quantity, 1)

    def test_add_to_cart_same_product(self):
        self.client.post(
            reverse("shop:add-to-cart", args=[self.product.pk]),
            {"quantity": 1}
        )
        self.client.post(
            reverse("shop:add-to-cart", args=[self.product.pk]),
            {"quantity": 4}
        )
        item = OrderItem.objects.get(product=self.product)
        self.assertEqual(item.quantity, 5)

    def test_quantity_cant_exceed_stock(self):
        self.client.post(
            reverse("shop:add-to-cart", args=[self.product.pk]),
            {"quantity": 30}
        )
        item = OrderItem.objects.get(product=self.product)
        self.assertEqual(item.quantity, 20)

    def test_quantity_less_or_zero_doesnt_exist(self):
        self.client.post(
            reverse("shop:add-to-cart", args=[self.product.pk]),
            {"quantity": 0}
        )
        self.assertFalse(Order.objects.exists())


class CartDetailTest(CartTestBase):
    def test_empty_cart(self):
        response = self.client.get(reverse("shop:cart-detail"))
        self.assertIsNone(response.context["order"])

    def test_cart_with_order(self):
        order = Order.objects.create(user=self.user, status="new")
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
        )
        response = self.client.get(reverse("shop:cart-detail"))
        self.assertEqual(response.context["order"], order)


class CartUpdateTest(CartTestBase):
    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(user=self.user, status="new")
        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=5,
        )

    def test_update_quantity(self):
        self.client.post(
            reverse("shop:cart-update", args=[self.item.pk]),
            {"quantity": 3}
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 3)

    def test_quantity_more_than_stock(self):
        self.client.post(
            reverse("shop:cart-update", args=[self.item.pk]),
            {"quantity": 30}
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 20)

    def test_quantity_less_or_zero_removes_item(self):
        self.client.post(
            reverse("shop:cart-update", args=[self.item.pk]),
            {"quantity": 0}
        )
        self.assertFalse(OrderItem.objects.exists())

    def test_not_user_cant_update_items(self):
        not_user = get_user_model().objects.create_user(
            username="NotUser1",
            password="notuser38631",
        )
        not_user_order = Order.objects.create(user=not_user, status="new")
        not_user_item = OrderItem.objects.create(
            order=not_user_order,
            product=self.product,
            quantity=1,
        )
        response = self.client.post(
            reverse("shop:cart-update", args=[not_user_item.pk]),
            {"quantity": 2}
        )
        self.assertEqual(response.status_code, 404)


class RemoveFromCartTest(CartTestBase):
    def test_remove_item(self):
        order = Order.objects.create(user=self.user, status="new")
        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=5,
        )

        self.client.post(
            reverse("shop:cart-remove", args=[item.pk]),
        )
        self.assertFalse(OrderItem.objects.exists())


class ConfirmOrderTest(CartTestBase):
    def test_confirm_order_success(self):
        order = Order.objects.create(user=self.user, status="new")
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=5,
        )
        self.client.post(reverse("shop:order-confirm"))
        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(order.status, "processing")
        self.assertEqual(self.product.stock_quantity, 15)

    def test_confirm_order_no_order(self):
        response = self.client.post(reverse("shop:order-confirm"))
        self.assertRedirects(response, reverse("shop:cart-detail"))

    def test_confirm_order_no_item_in_stock(self):
        order = Order.objects.create(user=self.user, status="new")
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=50,
        )
        self.client.post(reverse("shop:order-confirm"))
        order.refresh_from_db()
        self.assertEqual(order.status, "new")
