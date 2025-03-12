from django.shortcuts import render
from rest_framework import viewsets
from deliveries.models import Delivery 
print("Successfully imported Delivery model!")
from deliveries.serializers import DeliverySerializer

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()  # pylint: disable=no-member

    serializer_class = DeliverySerializer


# Create your views here.
