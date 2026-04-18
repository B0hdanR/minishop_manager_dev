from django.db.models import Sum, F
from shop.forms import OrderFilterForm, ProductFilterForm
from shop.models import Order, Product


class OrderFilterMixin:
    filter_from_class = OrderFilterForm

    def get_base_queryset(self):
        return (
            Order.objects.
            select_related("user").
            prefetch_related("items__product").
            annotate(total=Sum(F("items__quantity")*F("items__product__price")))
        )

    def get_queryset(self):
        queryset = self.get_base_queryset().order_by("-created_at")
        form = self.filter_from_class(self.request.GET)

        if form.is_valid():
            name = form.cleaned_data.get("name")
            status = form.cleaned_data.get("status")
            total_min = form.cleaned_data.get("total_min")
            total_max = form.cleaned_data.get("total_max")
            date_from = form.cleaned_data.get("date_from")
            date_to = form.cleaned_data.get("date_to")

            if name:
                if name.isdigit():
                    queryset = queryset.filter(id=int(name))
                else:
                    queryset = queryset.filter(user__username__icontains=name)


            if status:
                queryset = queryset.filter(status=status)

            if total_min is not None:
                queryset = queryset.filter(total__gte=total_min)
            if total_max is not None:
                queryset = queryset.filter(total__lte=total_max)

            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
        self.filter_form = form
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(
            self, "filter_form", self.filter_from_class()
        )
        return context


class ProductFilterMixin:
    filter_from_class = ProductFilterForm

    def get_queryset(self):
        queryset = Product.objects.select_related("category").order_by("id")
        form = self.filter_from_class(self.request.GET)

        if form.is_valid():
            name = form.cleaned_data.get("name")
            category = form.cleaned_data.get("category")
            price_min = form.cleaned_data.get("price_min")
            price_max = form.cleaned_data.get("price_max")

            if name:
                if name.isdigit():
                    queryset = queryset.filter(id=int(name))
                else:
                    queryset = queryset.filter(name__icontains=name)


            if category:
                queryset = queryset.filter(category=category)

            if price_min is not None:
                queryset = queryset.filter(price__gte=price_min)
            if price_max is not None:
                queryset = queryset.filter(price__lte=price_max)


        self.filter_form = form
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(
            self, "filter_form", self.filter_from_class()
        )
        return context


class BackUrlDetailMixin:
    def get_back_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.get_back_url()
        return context
