from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryViewSet

router = DefaultRouter()
router.register(r'deliveries', DeliveryViewSet)  # API endpoint: /api/deliveries/

urlpatterns = [
    path('api/', include(router.urls)),
    path("users/", include("users.urls")),
]
