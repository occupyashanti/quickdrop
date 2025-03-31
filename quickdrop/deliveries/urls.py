from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryViewSet, JobViewSet

router = DefaultRouter()
router.register(r'deliveries', DeliveryViewSet, basename='delivery')
router.register(r'jobs', JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]
