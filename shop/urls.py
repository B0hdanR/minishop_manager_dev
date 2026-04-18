from django.urls import path

from .views import (
    index,
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    OrderListView,
    ProductCategoryListView,
    ProductCategoryDetailView,
    ProductCategoryCreateView,
    ProductCategoryUpdateView,
    ProductCategoryDeleteView,
    add_to_cart,
    cart_detail,
    confirm_order,
    update_cart,
    remove_from_cart,
    OrderDetailView
)

urlpatterns = [
    path('', index, name='index'),
    path('products/', ProductListView.as_view(),
         name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(),
         name='product-detail'),
    path('products/create/', ProductCreateView.as_view(),
         name='product-create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(),
         name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(),
         name='product-delete'),

    path('orders/', OrderListView.as_view(),
         name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(),
         name='order-detail'),

    path('categories/', ProductCategoryListView.as_view(),
         name='productcategory-list'),
    path('categories/create/', ProductCategoryCreateView.as_view(),
         name='productcategory-create'),
    path('categories/<int:pk>/', ProductCategoryDetailView.as_view(),
         name='productcategory-detail'),
    path('categories/<int:pk>/update/', ProductCategoryUpdateView.as_view(),
         name='productcategory-update'),
    path('categories/<int:pk>/delete/', ProductCategoryDeleteView.as_view(),
         name='productcategory-delete'),

    path("cart/add/<int:pk>/", add_to_cart,
         name="add-to-cart"),
    path("cart/", cart_detail,
         name="cart-detail"),
    path("order/confirm/", confirm_order,
         name="order-confirm"),
    path("cart/update/<int:pk>/", update_cart,
         name="cart-update"),
    path("cart/remove/<int:pk>/", remove_from_cart,
         name="cart-remove"),
]

app_name = "shop"
