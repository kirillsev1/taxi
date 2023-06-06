"""Uls on views."""
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from rest_framework import routers
from taxi_manager import views

router = routers.DefaultRouter()
router.register('user', views.UserViewSet)
router.register('car', views.CarViewSet)
router.register('driver', views.DriverViewSet)
router.register('customer', views.PassengerViewSet)
router.register('order', views.OrderViewSet)

urlpatterns = [
    path('', views.index, name='homepage'),
    path('profile/', views.profile_page, name='profile'),
    path('customer_order/', views.order_page, name='order_page'),
    path('driver_order/', views.driver_order_page, name='driver_orders'),
    path('rest/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('driver_register/', views.driver_register, name='driver_register'),
    path('customer_register/', views.customer_register, name='customer_register'),
]
