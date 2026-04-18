from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic

from shop.mixins import OrderFilterMixin, BackUrlDetailMixin
from shop.models import Order
from .forms import SignUpForm, SupportRequestForm, UserUpdateForm
from django.contrib.auth import get_user_model

from .models import SupportRequest

User = get_user_model()


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # username = form.cleaned_data.get("username")
            # raw_password = form.cleaned_data.get("password1")
            # user = User.objects.create_user(username=username, password=raw_password)

            msg = 'Account created successfully.'
            success = True

            messages.success(request, "Account created successfully.")
            return redirect("accounts:login")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


class UserListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = User
    context_object_name = "user_list"
    template_name = "accounts/user_list.html"
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_employee


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, BackUrlDetailMixin, generic.DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "user_detail"

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_employee


class AccountUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/account_update.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "The changes were saved successfully.")
        return super().form_valid(form)


class MyOrderListView(LoginRequiredMixin, OrderFilterMixin, generic.ListView):
    model = Order
    paginate_by = 10
    template_name = "accounts/myorder_list.html"
    context_object_name = "myorder_list"
    ordering = ["-created_at"]

    def get_base_queryset(self):
        return super().get_base_queryset().filter(user=self.request.user).order_by("-created_at")

class MyOrderDetailView(LoginRequiredMixin, BackUrlDetailMixin, generic.DetailView):
    model = Order
    paginate_by = 20
    template_name = "accounts/myorder_detail.html"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = "accounts/profile.html"


class SupportCreateView(generic.CreateView):
    model = SupportRequest
    form_class = SupportRequestForm
    template_name = "accounts/support_form.html"
    success_url = reverse_lazy("shop:index")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user

        messages.success(self.request, "The message was sent successfully.")

        return super().form_valid(form)
