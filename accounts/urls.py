from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    register_user,
    MyOrderListView,
    ProfileView,
    MyOrderDetailView,
    UserListView, UserDetailView, SupportCreateView, AccountUpdateView
)

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'),
         name='login'),
    path('register/', register_user,
         name='register'),
    path('logout/', LogoutView.as_view(),
         name='logout'),

    path('myorders/', MyOrderListView.as_view(),
         name='myorder-list'),
    path('myorders/<int:pk>/', MyOrderDetailView.as_view(),
         name='myorder-detail'),

    path('profile/', ProfileView.as_view(),
         name='profile'),
    path('users/', UserListView.as_view(),
         name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(),
         name='user-detail'),
    path('account/', AccountUpdateView.as_view(),
         name='account-update'),

    path('support/', SupportCreateView.as_view(),
         name='support'),
]

app_name = "accounts"
