from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Delivery

User = get_user_model()

class DeliverySerializer(serializers.ModelSerializer):
    tracking_history = serializers.ListField(read_only=True)
    worker_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = [
            'id', 'order_id', 'tracking_id', 'status', 'created_at',
            'pickup_location', 'pickup_location_lat', 'pickup_location_lng',
            'delivery_location', 'delivery_location_lat', 'delivery_location_lng',
            'current_location_lat', 'current_location_lng',
            'estimated_delivery_time', 'actual_delivery_time',
            'customer', 'worker', 'worker_name', 'customer_name',
            'tracking_history'
        ]
        read_only_fields = ['tracking_id', 'worker', 'actual_delivery_time', 'tracking_history']

    def get_worker_name(self, obj):
        if obj.worker:
            return f"{obj.worker.first_name} {obj.worker.last_name}"
        return None

    def get_customer_name(self, obj):
        if obj.customer:
            return f"{obj.customer.first_name} {obj.customer.last_name}"
        return None

class JobSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    pickup_address = serializers.CharField(source='pickup_location', read_only=True)
    delivery_address = serializers.CharField(source='delivery_location', read_only=True)

    class Meta:
        model = Delivery
        fields = [
            'id', 'order_id', 'tracking_id', 'status',
            'pickup_address', 'pickup_location_lat', 'pickup_location_lng',
            'delivery_address', 'delivery_location_lat', 'delivery_location_lng',
            'estimated_delivery_time', 'customer_name'
        ]
        read_only_fields = ['tracking_id', 'status', 'estimated_delivery_time']

    def get_customer_name(self, obj):
        if obj.customer:
            return f"{obj.customer.first_name} {obj.customer.last_name}"
        return None
