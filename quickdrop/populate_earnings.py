import os
import sys
import django
import random
from decimal import Decimal
from datetime import timedelta, datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickdrop.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Earnings
from deliveries.models import Delivery

def populate_earnings():
    """
    Populate the Earnings table with sample data for workers
    based on their completed deliveries
    """
    # Get all workers (users with worker profile)
    workers = User.objects.filter(userprofile__user_type='worker')
    
    if not workers.exists():
        print("No workers found in the system.")
        return
    
    print(f"Found {workers.count()} workers. Populating earnings data...")
    
    # For each worker, create earnings records
    for worker in workers:
        # Get completed deliveries for this worker
        completed_deliveries = Delivery.objects.filter(
            assigned_driver=worker,
            status='DELIVERED'
        )
        
        if not completed_deliveries.exists():
            print(f"No completed deliveries found for {worker.username}")
            continue
        
        print(f"Creating earnings for {worker.username} based on {completed_deliveries.count()} deliveries")
        
        # Create an earning record for each completed delivery
        for delivery in completed_deliveries:
            # Base amount for delivery (between $8 and $15)
            base_amount = Decimal(str(random.uniform(8.0, 15.0))).quantize(Decimal('0.01'))
            
            # Create the delivery completion earning
            Earnings.objects.create(
                worker=worker,
                delivery=delivery,
                amount=base_amount,
                earning_type='DELIVERY',
                description=f"Delivery completion: {delivery.tracking_id}",
                timestamp=delivery.delivery_time or delivery.updated_at
            )
            
            # Add a tip for some deliveries (30% chance)
            if random.random() < 0.3:
                tip_amount = Decimal(str(random.uniform(1.0, 5.0))).quantize(Decimal('0.01'))
                Earnings.objects.create(
                    worker=worker,
                    delivery=delivery,
                    amount=tip_amount,
                    earning_type='TIP',
                    description=f"Customer tip for delivery: {delivery.tracking_id}",
                    timestamp=(delivery.delivery_time or delivery.updated_at) + timedelta(minutes=5)
                )
        
        # Add some performance bonuses (weekly)
        now = timezone.now()
        for week_back in range(4):  # Last 4 weeks
            if random.random() < 0.7:  # 70% chance of getting a weekly bonus
                bonus_date = now - timedelta(days=7*week_back)
                bonus_amount = Decimal(str(random.uniform(10.0, 30.0))).quantize(Decimal('0.01'))
                Earnings.objects.create(
                    worker=worker,
                    delivery=None,
                    amount=bonus_amount,
                    earning_type='BONUS',
                    description=f"Weekly performance bonus for {bonus_date.strftime('%Y-%m-%d')}",
                    timestamp=bonus_date
                )
    
    print("Earnings data population completed!")

if __name__ == '__main__':
    print("Starting earnings data population script...")
    populate_earnings()
    print("Done!")
