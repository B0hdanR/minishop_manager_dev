from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import F, Sum, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View, generic
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.contrib import messages

from shop.mixins import OrderFilterMixin, ProductFilterMixin, BackUrlDetailMixin
from shop.models import Product, Order, ProductCategory, OrderItem
from shop.forms import (
    ProductForm,
    OrderStatusUpdateForm,
    ProductCategorySearchForm,
    ProductCategoryForm
)


@login_required
def index(request):
    context = {
        "num_categories": ProductCategory.objects.count(),
        "num_products": Product.objects.count(),
        "num_users": get_user_model().objects.count(),
        "num_orders": Order.objects.count(),
        "num_myorders": Order.objects.filter(user=request.user).count() if request.user.is_authenticated else 0,
    }
    return render(request, 'shop/index.html', context=context)


class ProductListView(LoginRequiredMixin, ProductFilterMixin, generic.ListView):
    model = Product
    paginate_by = 10
    ordering = ["id"]


class ProductDetailView(LoginRequiredMixin, BackUrlDetailMixin, generic.DetailView):
    model = Product
    queryset = Product.objects.select_related("category")


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("shop:product-list")

    def test_func(self):
        return self.request.user.is_employee or self.request.user.is_staff


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("shop:product-list")

    def test_func(self):
        return self.request.user.is_employee or self.request.user.is_staff


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Product
    success_url = reverse_lazy("shop:product-list")

    def test_func(self):
        return self.request.user.is_employee or self.request.user.is_staff


class OrderListView(LoginRequiredMixin, UserPassesTestMixin, OrderFilterMixin, generic.ListView):
    model = Order
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_employee or self.request.user.is_staff


class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, BackUrlDetailMixin, generic.DetailView):
    model = Order
    queryset = Order.objects.prefetch_related("items__product")

    def test_func(self):
        return self.request.user.is_employee or self.request.user.is_staff

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context["form"] = OrderStatusUpdateForm(
            instance=self.object
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OrderStatusUpdateForm(request.POST, instance=self.object)

        if form.is_valid():
            form.save()
            return redirect("shop:order-detail", pk=self.object.pk)

        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class ProductCategoryListView(LoginRequiredMixin, generic.ListView):
    model = ProductCategory
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductCategoryListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = ProductCategorySearchForm(
            initial={"name": name}
        )
        return context

    def get_queryset(self):
        queryset = ProductCategory.objects.all().order_by("id")
        name = self.request.GET.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class ProductCategoryDetailView(LoginRequiredMixin, BackUrlDetailMixin, generic.DetailView):
    model = ProductCategory
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductCategoryDetailView, self).get_context_data(**kwargs)
        context["products"] = Product.objects.filter(category=self.object).select_related("category")
        return context


class ProductCategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    success_url = reverse_lazy("shop:productcategory-list")

    def test_func(self):
        return self.request.user.is_employee or self.request.user.is_staff


class ProductCategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    success_url = reverse_lazy("shop:productcategory-list")

    def test_func(self):
        return self.request.user.is_employee or self.request.user.is_staff


class ProductCategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = ProductCategory
    success_url = reverse_lazy("shop:productcategory-list")

    def test_func(self):
        return self.request.user.is_employee or self.request.user.is_staff


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get("quantity", 1))

    next_url = request.GET.get("next") or reverse("shop:product-list")

    if quantity > product.stock_quantity:
        quantity = product.stock_quantity
        messages.warning(
            request,
            f"{product.stock_quantity} items in stock"
        )

    if quantity <= 0:
        messages.error(request, "There must be at least 1.")
        return redirect(next_url)

    order, _ = Order.objects.get_or_create(
        user=request.user,
        status="new"
    )

    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
    )

    if created:
        order_item.quantity = quantity
    else:
        new_quantity = order_item.quantity + quantity
        if new_quantity > product.stock_quantity:
            order_item.quantity = product.stock_quantity
            messages.warning(
                request,
                f"{product.stock_quantity} items in stock"
            )
        else:
            order_item.quantity = new_quantity
    order_item.save()

    return redirect(next_url)


@login_required
def cart_detail(request):
    order = Order.objects.filter(
        user=request.user,
        status="new"
    ).prefetch_related("items__product").first()

    if order and order.status != "new":
        order = None

    return render(request, 'shop/cart_detail.html', {'order': order})


@login_required
@require_POST
def update_cart(request, pk):
    item = get_object_or_404(
        OrderItem,
        pk=pk,
        order__user=request.user,
        order__status="new"
    )

    quantity = int(request.POST.get("quantity", 1))

    if quantity <= 0:
        item.delete()
        messages.info(request, f"{item.product.name} removed from cart.")
        return redirect("shop:cart-detail")

    if quantity > item.product.stock_quantity:
        quantity = item.product.stock_quantity
        messages.warning(
            request,
            f"{item.product.stock_quantity} items in stock"
        )

    item.quantity = quantity
    item.save()

    return redirect("shop:cart-detail")


@login_required
@require_POST
def confirm_order(request):
    order = Order.objects.filter(
        user=request.user,
        status="new"
    ).prefetch_related("items__product").first()

    if not order:
        messages.error(request, "No order found.")
        return redirect("shop:cart-detail")

    for item in order.items.all():
        if item.quantity > item.product.stock_quantity:
            messages.error(
                request,
                f"{item.product.stock_quantity} items in stock for {item.product.name}"
            )
            return redirect("shop:cart-detail")

    with transaction.atomic():
        for item in order.items.all():
            product = item.product
            product.stock_quantity -= item.quantity
            product.save()

        order.status = "processing"
        order.save()

    messages.success(request, "Your order was successfully processed.")
    return redirect("accounts:myorder-list")


@login_required
@require_POST
def remove_from_cart(request, pk):
    item = get_object_or_404(
        OrderItem,
        pk=pk,
        order__user=request.user,
        order__status="new"
    )

    item.delete()
    return redirect("shop:cart-detail")
