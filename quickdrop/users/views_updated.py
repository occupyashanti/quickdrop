from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q, Avg, Sum
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from deliveries.models import Delivery
from .forms import UserRegisterForm, UserLoginForm
from .models import UserProfile, Earnings
import json
from django.core.mail import send_mail
import googlemaps
from datetime import timedelta

# Keep all existing functions unchanged, only modify the dashboard function
# for the worker dashboard section

@login_required(login_url='login')
def dashboard(request):
    user_type = request.user.userprofile.user_type
    
    if user_type == 'customer':
        # Customer Dashboard - unchanged
        active_deliveries = Delivery.objects.filter(
            customer=request.user,
            status__in=['PENDING', 'PICKED_UP', 'IN_TRANSIT']
        ).order_by('-created_at')

        context = {
            'active_deliveries': active_deliveries,
            'completed_deliveries': Delivery.objects.filter(
                customer=request.user,
                status='DELIVERED'
            ),
            'pending_deliveries': Delivery.objects.filter(
                customer=request.user,
                status='PENDING'
            ),
            'in_transit_deliveries': Delivery.objects.filter(
                customer=request.user,
                status='IN_TRANSIT'
            ),
            'active_tab': 'overview'
        }
        return render(request, 'users/customer_dashboard.html', context)
    
    else:
        # Worker Dashboard - updated to use Earnings model
        current_job = Delivery.objects.filter(
            assigned_driver=request.user,
            status__in=['PICKED_UP', 'IN_TRANSIT']
        ).first()

        # Get today's date range
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Get daily earnings
        daily_earnings = Earnings.objects.filter(
            worker=request.user,
            timestamp__gte=today_start,
            timestamp__lt=today_end
        ).order_by('-timestamp')
        
        daily_total = daily_earnings.aggregate(total=Sum('amount'))['total'] or 0
        
        # Get weekly earnings (last 7 days)
        week_start = today_start - timedelta(days=6)  # Last 7 days including today
        weekly_earnings = Earnings.objects.filter(
            worker=request.user,
            timestamp__gte=week_start,
            timestamp__lt=today_end
        )
        
        weekly_total = weekly_earnings.aggregate(total=Sum('amount'))['total'] or 0
        
        # Prepare weekly chart data
        weekly_data = []
        weekly_labels = []
        
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_end = day + timedelta(days=1)
            day_earnings = Earnings.objects.filter(
                worker=request.user,
                timestamp__gte=day,
                timestamp__lt=day_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            weekly_data.append(float(day_earnings))
            weekly_labels.append(day.strftime('%a'))
        
        # Get monthly earnings (last 30 days)
        month_start = today_start - timedelta(days=29)  # Last 30 days including today
        monthly_earnings = Earnings.objects.filter(
            worker=request.user,
            timestamp__gte=month_start,
            timestamp__lt=today_end
        )
        
        monthly_total = monthly_earnings.aggregate(total=Sum('amount'))['total'] or 0
        
        # Prepare monthly chart data
        monthly_data = []
        monthly_labels = []
        
        # Group by week for the monthly chart
        for i in range(0, 30, 7):
            week_start_date = month_start + timedelta(days=i)
            week_end_date = min(week_start_date + timedelta(days=7), today_end)
            week_earnings = Earnings.objects.filter(
                worker=request.user,
                timestamp__gte=week_start_date,
                timestamp__lt=week_end_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_data.append(float(week_earnings))
            monthly_labels.append(f"{week_start_date.strftime('%d %b')}-{(week_end_date - timedelta(days=1)).strftime('%d %b')}")
        
        # Calculate average completion time for delivered jobs
        delivered_jobs = Delivery.objects.filter(
            assigned_driver=request.user,
            status='DELIVERED',
            delivery_time__isnull=False
        )
        
        avg_completion_time = None
        if delivered_jobs.exists():
            total_time = timezone.timedelta()
            count = 0
            for job in delivered_jobs:
                if job.delivery_time and job.created_at:
                    total_time += job.delivery_time - job.created_at
                    count += 1
            if count > 0:
                avg_completion_time = total_time / count

        # Get available jobs
        available_jobs = Delivery.objects.filter(
            status='PENDING',
            assigned_driver__isnull=True
        ).order_by('-created_at')

        # Get job statistics
        job_stats = {
            'total_completed': delivered_jobs.count(),
            'total_cancelled': Delivery.objects.filter(
                assigned_driver=request.user,
                status='CANCELLED'
            ).count(),
            'avg_completion_time': avg_completion_time
        }

        context = {
            'current_job': current_job,
            'active_jobs': Delivery.objects.filter(
                assigned_driver=request.user,
                status__in=['PICKED_UP', 'IN_TRANSIT']
            ),
            'completed_jobs': delivered_jobs.order_by('-delivery_time')[:10],  # Last 10 completed jobs
            'available_jobs': available_jobs,
            'job_stats': job_stats,
            'earnings': daily_total,  # Today's earnings for the stats card
            'active_tab': 'overview',
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            # New earnings data for the earnings tab
            'daily_earnings': daily_earnings,
            'daily_total': daily_total,
            'weekly_earnings': weekly_earnings,
            'weekly_total': weekly_total,
            'monthly_earnings': monthly_earnings,
            'monthly_total': monthly_total,
            'weekly_labels': json.dumps(weekly_labels),
            'weekly_data': json.dumps(weekly_data),
            'monthly_labels': json.dumps(monthly_labels),
            'monthly_data': json.dumps(monthly_data),
            'today_date': timezone.now(),
        }
        return render(request, 'users/worker_dashboard.html', context)

# All other functions remain unchanged
