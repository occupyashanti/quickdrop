from rest_framework import serializers
from .models import Delivery

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'  # Or specify fields like ('id', 'order_id', 'status', 'created_at')
