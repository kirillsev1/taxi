from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'User', views.UserViewSet, basename="User")
router.register(r'Car', views.CarViewSet)
router.register(r'Driver', views.DriverViewSet)
router.register(r'Customer', views.PassengerViewSet)
router.register(r'Order', views.OrderViewSet, basename='order-list-create')
urlpatterns = [
    path('', views.index, name='homepage'),
    path('profile/', views.profile_page, name='profile'),
    path('order/', views.order_page, name='order_page'),
    path('driver_orders/', views.driver_order_page, name='driver_orders'),
    path('rest/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('driver_register/', views.driver_register, name='driver_register'),
    path('customer_register/', views.customer_register, name='customer_register'),
]
